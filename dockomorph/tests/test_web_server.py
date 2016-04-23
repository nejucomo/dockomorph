from mock import call, sentinel

from dockomorph.web.server import WebServer
from dockomorph.tests.logutil import LogMockingTestCase


class WebServerTests (LogMockingTestCase):
    def test_init_and_listen(self):
        m_Site = self.patch('twisted.web.server.Site')
        m_RootResource = self.patch('dockomorph.web.root.RootResource')
        m_reactor = self.make_mock()

        ws = WebServer(m_reactor)

        # Constructors shouldn't do (non-logging) I/O:
        self.assert_calls_equal(
            m_reactor,
            [])

        self.assert_calls_equal(
            m_RootResource,
            [call(m_reactor)])

        self.assert_calls_equal(
            m_Site,
            [call(m_RootResource())])

        self.reset_mocks()

        ws.listen(sentinel.PORT)

        self.assert_calls_equal(
            m_reactor,
            [call.listenTCP(sentinel.PORT, m_Site())])
