from mock import call

from dockomorph.web.root import RootResource
from dockomorph.tests.logutil import LogMockingTestCase


class RootResourceTests (LogMockingTestCase):
    def test__init__(self):
        m_File__init__ = self.patch('twisted.web.static.File.__init__')
        m_reactor = self.make_mock()

        rr = RootResource(m_reactor)

        self.assert_calls_equal(
            m_reactor,
            [])

        self.assert_calls_equal(
            m_File__init__,
            [call(rr, RootResource.StaticDir)])
