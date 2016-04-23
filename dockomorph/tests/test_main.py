from mock import MagicMock, sentinel, call

from dockomorph.main import main
from dockomorph.tests.logutil import LogMockingTestCase


class main_tests (LogMockingTestCase):
    def test_typical_run(self):
        m_parse_args = self.patch('dockomorph.clargs.parse_args')
        m_init = self.patch('dockomorph.log.init')
        m_reactor = MagicMock()

        result = main(sentinel.args, m_reactor)

        self.assertIs(result, None)

        self.assert_calls_equal(
            m_parse_args,
            [call(main.__doc__, sentinel.args)])

        self.assert_calls_equal(
            m_init,
            [call()])

        self.assert_calls_equal(
            m_reactor,
            [call.run()])
