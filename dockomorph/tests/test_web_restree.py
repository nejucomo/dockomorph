from mock import call, sentinel

from dockomorph.tests.logutil import LogMockingTestCase
from dockomorph.web.restree import build_resource_tree


class restreeTests (LogMockingTestCase):
    def setUp(self):
        LogMockingTestCase.setUp(self)

        self.m_Resource = self.patch('twisted.web.resource.Resource')

    def test_build_resource_tree_empty(self):
        m_res = self.make_mock()

        self._build_resource_tree(m_res, {})

        self.assert_calls_equal(
            m_res,
            [])

        self.assertNoResourceCreated()

    def test_build_resource_tree_non_recursive(self):
        m_res = self.make_mock()

        self._build_resource_tree(m_res, {'c': sentinel.CHILD})

        self.assert_calls_equal(
            m_res,
            [call.putChild('c', sentinel.CHILD)])

        self.assertNoResourceCreated()

    def test_build_resource_tree_recursive(self):
        m_res = self.make_mock()

        self._build_resource_tree(
            m_res,
            {'c': sentinel.CHILD,
             'sub': {'gc': sentinel.GRANDCHILD}})

        self.assert_calls_equal(
            m_res,
            [call.putChild('c', sentinel.CHILD),
             call.putChild('sub', self.m_Resource.return_value)])

        self.assert_calls_equal(
            self.m_Resource,
            [call(),
             call().putChild('gc', sentinel.GRANDCHILD)])

    def _build_resource_tree(self, resource, children):
        ret = build_resource_tree(resource, children)
        self.assertIs(resource, ret)
        self.assertFalse(resource.isLeaf)

    def assertNoResourceCreated(self):
        self.assert_calls_equal(
            self.m_Resource,
            [])
