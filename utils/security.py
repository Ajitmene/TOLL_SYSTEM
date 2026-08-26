"""
Lightweight password hashing helpers.

Uses salted SHA-256 (via hashlib.pbkdf2_hmac) which needs no third
party dependency, keeping the project dependency-free while still
avoiding plaintext password storage.
"""

import hashlib
import os


_ITERATIONS = 100_000


def hash_password(plain_password, salt=None):
    """Return a 'salt$hash' string for the given plaintext password."""

    if salt is None:
        salt = os.urandom(16).hex()

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        _ITERATIONS
    ).hex()

    return f"{salt}${derived}"


def verify_password(plain_password, stored_hash):
    """Check a plaintext password against a stored 'salt$hash' value."""

    if not stored_hash or "$" not in stored_hash:
        return False

    salt, _ = stored_hash.split("$", 1)

    return hash_password(plain_password, salt) == stored_hash
