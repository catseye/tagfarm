import json
import os
import sys
from tempfile import mkdtemp
import unittest
from subprocess import check_call

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
assert StringIO

from tagfarm.main import main


class TestTagfarm(unittest.TestCase):

    def setUp(self):
        super(TestTagfarm, self).setUp()
        self.saved_stdout = sys.stdout
        self.saved_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        self.maxDiff = None
        self.dirname = mkdtemp()
        self.prevdir = os.getcwd()
        os.chdir(self.dirname)
        check_call("mkdir -p by-tag", shell=True)

    def tearDown(self):
        os.chdir(self.prevdir)
        check_call("rm -rf {}".format(self.dirname), shell=True)
        sys.stdout = self.saved_stdout
        sys.stderr = self.saved_stderr
        super(TestTagfarm, self).tearDown()

    def test_media_root_not_found(self):
        check_call("rm -rf by-tag", shell=True)
        with self.assertRaises(ValueError):
            main(['backup.json'])

    def test_failure(self):
        with self.assertRaises(SystemExit):
            main(['backup.json'])


if __name__ == '__main__':
    unittest.main()
