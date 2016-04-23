import sys
import logging

from mock import call

from dockomorph import log
from dockomorph.tests.logutil import LogMockingTestCase, ArgIsLogRecord


class init_tests (LogMockingTestCase):
    def test_init(self):
        m_basicConfig = self.patch('logging.basicConfig')
        m_PLO = self.patch('twisted.python.log.PythonLoggingObserver')

        log.init()

        self.assert_calls_equal(
            m_basicConfig,
            [call(
                stream=sys.stdout,
                format=log.LogFormat,
                datefmt=log.DateFormat,
                level=logging.DEBUG)])

        self.assert_calls_equal(
            m_PLO,
            [call(),
             call().start()])

        self.assert_calls_equal(
            self.m_loghandler,
            [])


class LogMixinTests (LogMockingTestCase):
    def _test_init_and_name(self, name, instanceinfo):
        class MyClass (log.LogMixin):
            def __init__(self):
                log.LogMixin.__init__(self, instanceinfo)

        obj = MyClass()

        self.assertEqual(obj._log.name, name)

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(ArgIsLogRecord(msg='__init__'))])

    def test__init__without_instanceinfo(self):
        self._test_init_and_name('MyClass', None)

    def test__init__with_instanceinfo(self):
        self._test_init_and_name('MyClass[42]', 42)
