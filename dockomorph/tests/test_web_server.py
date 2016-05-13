from mock import call, sentinel

from dockomorph.web.server import WebServer
from dockomorph.tests.logutil import LogMockingTestCase


class WebServerTests (LogMockingTestCase):
    def test_init_and_listen(self):
        m_Site = self.patch('twisted.web.server.Site')
        m_File = self.patch('twisted.web.static.File')
        m_reactor = self.make_mock()

        ws = WebServer(m_reactor)

        # Constructors shouldn't do (non-logging) I/O:
        self.assert_calls_equal(
            m_reactor,
            [])

        self.assert_calls_equal(
            m_File,
            [call(WebServer.StaticDir)])

        self.assert_calls_equal(
            m_Site,
            [call(m_File())])

        self.reset_mocks()

        ws.listen(sentinel.PORT)

        self.assert_calls_equal(
            m_reactor,
            [call.listenTCP(sentinel.PORT, m_Site())])
