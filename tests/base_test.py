"""
Shared base class for tests: redirects data/ and logs/ to a
temporary directory for the duration of each test so tests never
touch (or depend on) the developer's real JSON data files.
"""

import os
import shutil
import tempfile
import unittest


class BaseTollTestCase(unittest.TestCase):

    def setUp(self):
        self._original_cwd = os.getcwd()
        self._tmp_dir = tempfile.mkdtemp(prefix="toll_system_test_")

        os.chdir(self._tmp_dir)
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

    def tearDown(self):
        os.chdir(self._original_cwd)
        shutil.rmtree(self._tmp_dir, ignore_errors=True)
