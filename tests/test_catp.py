import codecs
import io
import pickle
import re
import subprocess
import tempfile
import unittest

import catp


def _write_pickles_native_objs(buffer):
    for i in range(2):
        pickle.dump((i, 2*i), buffer)
    buffer.flush()


class TestCatp(unittest.TestCase):

    def setUp(self):
        self._pickle_here = tempfile.NamedTemporaryFile(mode='a+b')
        self._out_here = tempfile.TemporaryFile(mode='a+b')
        _write_pickles_native_objs(self._pickle_here)

    def tearDown(self):
        self._pickle_here.close()
        del self._pickle_here

    def test_read_routine(self):
        collection = catp.catp([self._pickle_here.name], self._out_here)

        self._out_here.seek(0)
        d = pickle.load(self._out_here)

        self.assertEqual(
            d,
            [(0, 0), (1, 2)],
        )
        self.assertEqual(
            collection,
            [(0, 0), (1, 2)],
        )

    def test_run_script_write_to_stdout(self):
        completion = subprocess.run(
            ["catp.py", self._pickle_here.name],
            capture_output=True,
        )

        completion.check_returncode()

        # stdout
        stdout = io.BytesIO(completion.stdout)
        collection = pickle.load(stdout)
        self.assertEqual(
            collection,
            [(0, 0), (1, 2)],
        )

        # logs
        stderr = io.BytesIO(completion.stderr)
        stderr = codecs.decode(stderr.getvalue())
        stderr = stderr.split("\n")
        log_prefix = r'INFO:__main__:'
        read_pattern = log_prefix + r'read from pickle file \S'
        match0 = re.match(read_pattern, stderr[0])
        self.assertTrue(match0)
        wrote_pattern = (
            log_prefix + r'wrote a total of 2 objects to \S'
        )
        match1 = re.match(wrote_pattern, stderr[1])
        self.assertTrue(match1)
