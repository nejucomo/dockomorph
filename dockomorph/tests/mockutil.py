from pprint import pformat
from twisted.trial import unittest
import mock


class MockingTestCase (unittest.TestCase):
    def setUp(self):
        self._mockset = []

    def patch(self, name):
        p = mock.patch(name)
        self.addCleanup(p.stop)
        m = p.start()
        self._mockset.append(m)
        return m

    def make_mock(self):
        m = mock.MagicMock()
        self._mockset.append(m)
        return m

    def reset_mocks(self):
        for m in self._mockset:
            m.reset_mock()

    def assert_calls_equal(self, mockobj, expectedcalls):
        mockcalls = mockobj._mock_mock_calls
        self.assertEqual(
            len(mockcalls), len(expectedcalls),
            'len(%s) == %r != len(%s) == %r' % (
                pformat(mockcalls), len(mockcalls),
                pformat(expectedcalls), len(expectedcalls)))

        loopelems = enumerate(zip(mockcalls, expectedcalls))
        for i, (mockcall, expectedcall) in loopelems:
            try:
                self.assertEqual(
                    mockcall, expectedcall,
                    'Arg {:d}:\n{}\n  !=\n{}'.format(
                        i,
                        pformat(mockcall),
                        pformat(expectedcall)))
            except AssertionError, e:
                raise
            except Exception, e:
                e.args += (
                    'Internal unittesting exception; vars:',
                    i,
                    mockcall,
                    expectedcall)
                raise


class EqCallback (object):
    """
    I am useful for making assert_calls_equal checks which are more
    flexible than standard ==.
    """
    def __init__(self, eqcb, repstr=None):
        if repstr is None:
            if eqcb.__doc__:
                repstr = eqcb.__doc__
            elif eqcb.__name__:
                repstr = eqcb.__name__
            else:
                repstr = repr(eqcb)

        self._eqcb = eqcb
        self._repstr = repstr

    def __eq__(self, other):
        return self._eqcb(other)

    def __repr__(self):
        return self._repstr


ArgIsType = lambda T: EqCallback(
    lambda v: isinstance(v, T),
    'ArgIsType({})'.format(T.__name__,))


def ArgIsTypeWithAttrs(T, **attrs):
    desc = 'ArgIsLogTypeWithAttrs({}, {})'.format(
        T.__name__,
        ', '.join(
            '{}={!r}'.format(k, v)
            for (k, v)
            in attrs.iteritems()))

    def check_arg(x):
        if not isinstance(x, T):
            return False

        for (name, expected) in attrs.iteritems():
            actual = getattr(x, name)
            if expected != actual:
                return False

        return True

    return EqCallback(check_arg, desc)
