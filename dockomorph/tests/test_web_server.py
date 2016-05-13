from mock import call, sentinel

from dockomorph.web.server import WebServer
from dockomorph.tests.logutil import LogMockingTestCase


class WebServerTests (LogMockingTestCase):
    def test_init_and_listen(self):
        m_Site = self.patch('twisted.web.server.Site')
        m_File = self.patch('twisted.web.static.File')
        m_brt = self.patch('dockomorph.web.restree.build_resource_tree')
        m_ghwr = self.patch('dockomorph.web.github.WebhookResource')
        m_reactor = self.make_mock()

        ws = WebServer(m_reactor, sentinel.SECRET, sentinel.CALLBACK)

        # Constructors shouldn't do (non-logging) I/O:
        self.assert_calls_equal(
            m_reactor,
            [])

        self.assert_calls_equal(
            m_File,
            [call(WebServer.StaticDir)])

        self.assert_calls_equal(
            m_ghwr,
            [call(sentinel.SECRET, sentinel.CALLBACK)])

        self.assert_calls_equal(
            m_brt,
            [call(m_File(), {'api': {'github': m_ghwr()}})])

        self.assert_calls_equal(
            m_Site,
            [call(m_brt())])

        self.assertFalse(m_Site().displayTracebacks)

        self.reset_mocks()

        ws.listen(sentinel.PORT)

        self.assert_calls_equal(
            m_reactor,
            [call.listenTCP(sentinel.PORT, m_Site())])
