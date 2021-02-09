"""Tests for `grep.py`.
"""
import subprocess
import unittest

import grep


class TestGrep(unittest.TestCase):

    def test_true(self):
        return True

    def test_simple_callable(self):
        completion = subprocess.run(
            ["grep.py", self._pickle_here.name],
            capture_output=True,
        )
        
