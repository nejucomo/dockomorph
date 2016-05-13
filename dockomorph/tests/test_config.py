from mock import call, sentinel

from dockomorph import config
from dockomorph.tests.logutil import LogMockingTestCase


class parse_config_tests (LogMockingTestCase):
    def test_parse_config(self):
        m_RCP = self.patch('ConfigParser.RawConfigParser')

        m_RCP.return_value.sections.return_value = ['a', 'b', 'c']
        m_RCP.return_value.items.side_effect = lambda s: ('section', s)

        conf = config.parse_config(sentinel.PATH)

        self.assert_calls_equal(
            m_RCP,
            [call(),
             call().read(sentinel.PATH),
             call().sections(),
             call().items('a'),
             call().items('b'),
             call().items('c')])

        self.assertEqual(
            conf,
            {'a': ('section', 'a'),
             'b': ('section', 'b'),
             'c': ('section', 'c')})
