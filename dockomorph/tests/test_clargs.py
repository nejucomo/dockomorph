import argparse

from dockomorph import clargs
from dockomorph.tests.logutil import LogMockingTestCase


class parse_args_tests (LogMockingTestCase):
    def test_help(self):
        self.assertRaises(SystemExit, clargs.parse_args, 'banana', ['--help'])

    def test_no_args(self):
        opts = clargs.parse_args('banana', [])
        self.assertEqual(opts, argparse.Namespace(port=8080))

    def test_port(self):
        opts = clargs.parse_args('wombat', ['--port', '42'])
        self.assertEqual(opts, argparse.Namespace(port=42))

    def test_unexpected_args(self):
        self.assertRaises(SystemExit, clargs.parse_args, 'banana', ['slug'])
