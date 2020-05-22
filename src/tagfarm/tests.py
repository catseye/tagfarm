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

    def test_tag(self):
        check_call("touch content1", shell=True)
        check_call("touch content2", shell=True)
        main(['tag', 'blixit', 'content1', 'content2'])
        main(['tag', 'flonk', 'content1'])

        self.assertEqual(os.readlink(os.path.join('by-tag', 'blixit', 'content1')), '../../content1')
        self.assertEqual(os.readlink(os.path.join('by-tag', 'blixit', 'content2')), '../../content2')

        self.assertEqual(os.readlink(os.path.join('by-tag', 'flonk', 'content1')), '../../content1')
        self.assertFalse(os.path.exists(os.path.join('by-tag', 'flonk', 'content2')))
        self.assertFalse(os.path.lexists(os.path.join('by-tag', 'flonk', 'content2')))

    def test_untag(self):
        check_call("touch content1", shell=True)
        check_call("touch content2", shell=True)
        main(['tag', 'blixit', 'content1', 'content2'])
        main(['tag', 'flonk', 'content1'])

        main(['untag', 'blixit', 'content1', 'content2'])
        main(['untag', 'flonk', 'content2'])

        self.assertFalse(os.path.exists(os.path.join('by-tag', 'blixit', 'content1')))
        self.assertFalse(os.path.lexists(os.path.join('by-tag', 'blixit', 'content1')))

        self.assertFalse(os.path.exists(os.path.join('by-tag', 'blixit', 'content2')))
        self.assertFalse(os.path.lexists(os.path.join('by-tag', 'blixit', 'content2')))

        self.assertEqual(os.readlink(os.path.join('by-tag', 'flonk', 'content1')), '../../content1')

        self.assertFalse(os.path.exists(os.path.join('by-tag', 'flonk', 'content2')))
        self.assertFalse(os.path.lexists(os.path.join('by-tag', 'flonk', 'content2')))

    def test_repair(self):
        check_call("mkdir -p subdir1", shell=True)
        check_call("mkdir -p subdir2", shell=True)
        check_call("touch subdir1/content1", shell=True)

        main(['tag', 'blixit', 'subdir1/content1'])

        self.assertEqual(os.readlink(os.path.join('by-tag', 'blixit', 'content1')), '../../subdir1/content1')

        check_call("mv subdir1/content1 subdir2/content1", shell=True)

        self.assertFalse(os.path.exists(os.path.join('by-tag', 'blixit', 'content1')))
        self.assertTrue(os.path.lexists(os.path.join('by-tag', 'blixit', 'content1')))

        self.assertEqual(os.readlink(os.path.join('by-tag', 'blixit', 'content1')), '../../subdir1/content1')

        main(['repair'])

        self.assertEqual(os.readlink(os.path.join('by-tag', 'blixit', 'content1')), '../../subdir2/content1')


if __name__ == '__main__':
    unittest.main()
