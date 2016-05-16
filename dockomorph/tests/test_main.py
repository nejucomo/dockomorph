from mock import ANY, sentinel, call

from dockomorph.main import main
from dockomorph.tests.logutil import LogMockingTestCase


class main_tests (LogMockingTestCase):
    def test_typical_run(self):
        m_parse_args = self.patch('dockomorph.clargs.parse_args')
        m_parse_config = self.patch('dockomorph.config.parse_config')
        m_cols = self.patch('dockomorph.secrets.create_or_load_secret')
        m_init = self.patch('dockomorph.log.init')
        m_WebServer = self.patch('dockomorph.web.server.WebServer')
        m_reactor = self.make_mock()

        m_parse_config.return_value = {
            'github': {
                'secret': sentinel.GH_SECRET,
            },
        }

        result = main(sentinel.args, m_reactor)

        self.assertIs(result, None)

        self.assert_calls_equal(
            m_parse_args,
            [call(main.__doc__, sentinel.args)])

        self.assert_calls_equal(
            m_init,
            [call()])

        self.assert_calls_equal(
            m_cols,
            [call('github')])

        self.assert_calls_equal(
            m_WebServer,
            [call(m_reactor, m_cols.return_value, ANY),
             call().listen(m_parse_args().port)])

        self.assert_calls_equal(
            m_reactor,
            [call.run()])
