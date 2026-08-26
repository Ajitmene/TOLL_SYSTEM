# Smart Toll Booth Collection & Traffic Management System

A layered, object-oriented Python application that simulates a real
toll plaza network: vehicle registration, role-based staff logins,
toll calculation, cash/UPI/card/FASTag/prepaid-pass payments,
violation tracking across multiple booths, and daily analytics —
all persisted to a lightweight JSON "database" with zero third-party
dependencies.

Run it from the command line and it behaves like the kind of system
an actual toll plaza operator would log into every morning.

```
python main.py
```

Default bootstrap login (created automatically the first time the
app runs against an empty `data/users.json`):

```
username: admin
password: admin123
```

---

## Table of contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting started](#getting-started)
- [Project layout](#project-layout)
- [Roles & permissions](#roles--permissions)
- [Toll pricing](#toll-pricing)
- [Testing](#testing)
- [Design notes](#design-notes)

---

## Features

| Phase | Capability |
|---|---|
| 1 | Layered architecture: `models` → `repositories` → `services` → `main.py` |
| 2 | OOP domain models with inheritance & polymorphism (`User`/`Admin`/`Manager`/`TollOperator`, `PaymentMethod` subclasses) |
| 3 | A generic JSON-file repository layer standing in for a database |
| 4 | Login, salted-hash passwords, and role-based method decorators |
| 5 | Vehicle registration, lookup, update, and deletion with format validation |
| 6 | Toll calculation engine — base rate, peak-hour surcharge, FASTag discount |
| 7 | Cash / UPI / Card / FASTag payments, FASTag balance management |
| 8 | Prepaid Monthly and Trip toll passes |
| 9 | Automatic violation logging (missing tag, insufficient balance) with fines |
| 10 | Multiple toll booths/lanes with network-wide load & status reporting |
| 11 | Revenue, vehicle-type, and booth analytics, exportable to JSON/CSV |
| 12 | Centralized logging (`logs/system.log`) and a custom exception hierarchy |
| 13 | 68 unit/integration tests (`unittest`, no external test runner required) |
| 14 | Dependency-free standard-library implementation + this README |

## Architecture

```
main.py  (CLI / presentation layer)
   |
   v
services/       - business logic, one class per capability
   |             (VehicleService, TollService, FASTagService,
   |              PassService, ViolationService, TollBoothService,
   |              BoothNetworkService, AuthService, UserService,
   |              PaymentService, TransactionService, ReportService,
   |              TollCrossingService - the orchestrator)
   v
repositories/   - thin CRUD wrappers, one per JSON file
   v
data/*.json     - the "database"
```

`models/` holds plain OOP domain classes (`Vehicle`, `FASTag`,
`TollBooth`, `Transaction`, `TollPass`, `Violation`, `User` and its
subclasses, and the `PaymentMethod` hierarchy). Services translate
between these objects and the dict shape stored in JSON.

`TollCrossingService` is the one place that ties every phase
together: given a vehicle, booth, operator, and payment method, it
looks up the vehicle, calculates the toll, charges the chosen
payment method (or consumes a prepaid pass), logs a `Transaction`,
updates the booth's running stats, and -- if payment fails because
of a missing/underfunded FASTag -- automatically opens a `Violation`
record with a fine.

## Getting started

Requires only Python 3.8+. No installation step needed.

```bash
python main.py
```

On first run (empty `data/users.json`) the app seeds a default
`admin` / `admin123` account so you have somewhere to start; create
Manager and Toll Operator accounts from the Admin menu afterwards.

A typical first session:

1. Log in as `admin`.
2. Create a toll booth (menu 7).
3. Register a vehicle (menu 1).
4. Issue it a FASTag or a toll pass (menus 4 / 6).
5. Process a crossing at the booth you created (menu 9).
6. View the daily report (menu 12 -> 1).

## Web console

A full browser-based admin dashboard is included in `webapp/` — it's
a thin Flask front end over the exact same `services/` layer the
CLI uses, so every phase of the project (auth/roles, vehicles,
booths, FASTag/pass payments, violations, reports) is available as
a proper UI, not just a menu.

```bash
pip install flask
python webapp/app.py
```

Then open **http://127.0.0.1:5000** and sign in with `admin` /
`admin123` (seeded automatically on first run, same as the CLI).

What you get:

- A login screen and a sidebar-navigated dashboard with live stat
  cards (collections, vehicles processed, open booths, outstanding
  fines) and a revenue-by-vehicle-type breakdown.
- **Process Crossing** — the core operational screen: pick a
  vehicle, an open booth, and a payment method (Cash/UPI/Card/
  FASTag/Pass) and get a receipt back inline.
- Full CRUD-style pages for **Vehicles**, **Toll Booths**,
  **FASTags**, **Toll Passes**, **Violations**, and (Admin-only)
  **Staff & Users** — each with search, status badges, and inline
  action buttons (recharge, open/close a booth, pay/waive a fine,
  activate/deactivate an account).
- A **Reports & Analytics** page with revenue-by-booth and
  revenue-by-payment-method tables, plus one-click JSON/CSV export.
- The same role-based permission rules as the CLI, enforced in the
  route layer (`@roles_required(...)` in `webapp/app.py`) on top of
  the service-layer `@require_role` checks — a Toll Operator simply
  won't see the Admin-only pages or actions.

The web UI has no separate data model — it reads and writes the
same `data/*.json` files as `main.py`, so you can freely switch
between the CLI and the browser against the same running system.

For a real deployment, run it behind a production WSGI server (e.g.
`gunicorn webapp.app:app`) instead of the built-in `app.run(debug=True)`,
and set `TOLL_SECRET_KEY` to a random value.

## Project layout

```
config/settings.py         toll rates, peak hours, discounts, currency symbol
models/                    Vehicle, FASTag, TollBooth, Transaction,
                            TollPass, Violation, User/Admin/Manager/
                            TollOperator, PaymentMethod subclasses
repositories/               JSONRepository base + one repo per entity
services/                   one service class per business capability
reports/                    daily_report.py (console) and
                            report_generator.py (JSON/CSV export)
utils/                      logger, custom exceptions, decorators,
                            validators, id/password helpers
data/                       JSON "database" files (seed data included)
logs/system.log             audit/action log, created on first run
tests/                      unittest suite, one file per service
webapp/                     Flask web console (app.py, templates/, static/)
main.py                     CLI entry point
```

## Roles & permissions

| Role | Can do |
|---|---|
| **Admin** | Everything: manage users, vehicles, booths, FASTags, passes, violations, and reports |
| **Manager** | Read-only: view vehicles, booth status, violations, and reports |
| **Toll Operator** | Register vehicles and process crossings at their assigned booth |

Role checks are enforced in the service layer itself via the
`@require_role(...)` decorator in `utils/decorators.py`, not just in
the CLI -- so the rule holds no matter what calls the service.

## Toll pricing

Configured in `config/settings.py`:

- Base rate by vehicle type (Bike/Car/SUV/LCV/Bus/Truck/Multi-Axle)
- A peak-hour surcharge for two daily windows (08:00-10:00, 17:00-20:00)
- A 10% discount on FASTag payments
- Monthly and per-trip prepaid pass pricing in `services/pass_service.py`
- Default violation fines in `services/violation_service.py`

## Testing

```bash
python -m unittest discover -s tests -v
```

68 tests across 9 files cover vehicle management, toll calculation,
payments, FASTag balances, prepaid passes, violations, multi-booth
operations, auth/roles, and the end-to-end crossing flow. Each test
runs in an isolated temporary `data/`/`logs/` directory (see
`tests/base_test.py`), so running the suite never touches your real
JSON data.

## Design notes

- **No external dependencies.** Persistence is plain JSON files via
  a small repository layer, so the whole thing runs with a stock
  Python install.
- **Custom exception hierarchy** (`utils/exceptions.py`) -- every
  domain error (e.g. `InsufficientBalanceError`,
  `VehicleNotFoundError`, `AuthorizationError`) inherits from both a
  common `TollSystemError` and `ValueError`, so callers can catch
  broadly or precisely.
- **Passwords are never stored in plaintext** -- `utils/security.py`
  salts and hashes with PBKDF2-HMAC-SHA256.
- **Centralized logging** -- every service action and failure is
  written to `logs/system.log` via `utils/logger.py`, independent of
  whatever the CLI prints to the screen.
