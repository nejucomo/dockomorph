from mock import call, sentinel

from dockomorph.web.root import RootResource
from dockomorph.tests.logutil import LogMockingTestCase


class RootResourceTests (LogMockingTestCase):
    def setUp(self):
        LogMockingTestCase.setUp(self)

        self.m_File = self.patch('twisted.web.static.File')
        self.m_reactor = self.make_mock()

        self.rr = RootResource(self.m_reactor)

    def test__init__(self):
        self.assert_calls_equal(
            self.m_reactor,
            [])

        self.assert_calls_equal(
            self.m_File,
            [call(RootResource.StaticDir)])

    def test_getChild_delegates_to_statres(self):
        m_statres = self.make_mock()
        self.rr._statres = m_statres

        result = self.rr.getChild(sentinel.path, sentinel.request)

        self.assert_calls_equal(
            self.m_reactor,
            [])

        self.assert_calls_equal(
            m_statres,
            [call.getChild(sentinel.path, sentinel.request)])

        self.assertIs(result, m_statres.getChild.return_value)
