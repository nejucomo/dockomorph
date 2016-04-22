import logging

from dockomorph.tests.mockutil import MockingTestCase, ArgIsTypeWithAttrs


class LogMockingTestCase (MockingTestCase):
    def setUp(self):
        MockingTestCase.setUp(self)

        self.m_loghandler = self.make_mock()
        self.m_loghandler.level = logging.DEBUG

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(self.m_loghandler)

        self.addCleanup(root.removeHandler, self.m_loghandler)

        # A monkeypatch hack to improve the diagnostic utility of
        # LogRecord mismatches in test failures:
        original_repr = logging.LogRecord.__repr__
        logging.LogRecord.__repr__ = logging.LogRecord.__str__

        self.addCleanup(setattr, logging.LogRecord, '__repr__', original_repr)


def ArgIsLogRecord(**attrs):
    return ArgIsTypeWithAttrs(logging.LogRecord, **attrs)
