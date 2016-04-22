from mock import call

from dockomorph.log import LogMixin
from dockomorph.tests.logutil import LogMockingTestCase, ArgIsLogRecord


class LogMixinTests (LogMockingTestCase):
    def _test_init_and_name(self, name, instanceinfo):
        class MyClass (LogMixin):
            def __init__(self):
                LogMixin.__init__(self, instanceinfo)

        obj = MyClass()

        self.assertEqual(obj._log.name, name)

        self.assert_calls_equal(
            self.m_loghandler,
            [call.handle(ArgIsLogRecord(msg='__init__'))])

    def test_LogMixin_subclass_without_instanceinfo(self):
        self._test_init_and_name('MyClass', None)

    def test_LogMixin_subclass_with_instanceinfo(self):
        self._test_init_and_name('MyClass[42]', 42)
