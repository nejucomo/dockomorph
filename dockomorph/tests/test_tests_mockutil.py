import unittest
from mock import call, sentinel

from dockomorph.tests.mockutil import \
    ArgIsType, \
    ArgIsTypeWithAttrs, \
    EqCallback, \
    MockingTestCase


class MockingTestCaseTests (MockingTestCase):
    def test_assert_calls_equal_ok_empty(self):
        m = self.make_mock()
        self.assert_calls_equal(m, [])

    def test_assert_calls_equal_ok_nonemtpy(self):
        m = self.make_mock()
        m(sentinel.arg)
        self.assert_calls_equal(m, [call(sentinel.arg)])

    def test_assert_calls_equal_bad_nonequal(self):
        m = self.make_mock()
        m(sentinel.arg)

        self.assertRaises(
            AssertionError,
            self.assert_calls_equal,
            m,
            [call(sentinel.another_arg)])

    def test_assert_calls_equal_bad_eq_exception(self):
        m = self.make_mock()
        m(sentinel.arg)

        self.assertRaises(
            TypeError,
            self.assert_calls_equal,
            m,
            [call(EqCallback(lambda _: () + 42))])


class EqCallbackTests (unittest.TestCase):
    def test__eq__(self):
        eqcb = EqCallback(lambda x: x % 2 == 0)

        self.assertEqual(eqcb, 0)
        self.assertEqual(eqcb, 2)
        self.assertNotEqual(eqcb, 1)
        self.assertNotEqual(eqcb, 3)

    def test_default_name__doc__(self):
        def compare(thing):
            """thing is 42"""
            return thing is 42

        # Sanity check and code coverage:
        self.assertTrue(compare(42))

        eqcb = EqCallback(compare)

        self.assertEqual(
            '<EqCallback {}>'.format(compare.__doc__),
            repr(eqcb))

    def test_default_name__name__(self):
        eqcb = EqCallback(lambda _: False)

        # Sanity check and code coverage:
        self.assertNotEqual(42, eqcb)

        self.assertEqual('<EqCallback <lambda>>', repr(eqcb))

    def test_default_name__repr__(self):
        class C (object):
            pass

        i = C()

        eqcb = EqCallback(i)

        self.assertEqual(
            '<EqCallback {!r}>'.format(i),
            repr(eqcb))


class ArgIsTypeTests (unittest.TestCase):
    def setUp(self):
        self.eqcb = ArgIsType(int)

    def test_ok(self):
        self.assertEqual(self.eqcb, 0)
        self.assertEqual(self.eqcb, 42)

    def test_bad_type(self):
        self.assertNotEqual(self.eqcb, 3.14)
        self.assertNotEqual(self.eqcb, 'Banana')


class ArgIsTypeWithAttrsTests (unittest.TestCase):
    def setUp(self):
        class C (object):
            x = 42
            y = 'banana'

        self.C = C

    def test_ok(self):
        eqcb = ArgIsTypeWithAttrs(self.C, x=42, y='banana')
        self.assertEqual(self.C(), eqcb)

    def test_ok_attr_subset(self):
        eqcb = ArgIsTypeWithAttrs(self.C, x=42)
        self.assertEqual(self.C(), eqcb)

    def test_bad_type(self):
        eqcb = ArgIsTypeWithAttrs(self.C, x=42, y='banana')
        self.assertNotEqual(42, eqcb)

    def test_bad_attr_unequal(self):
        eqcb = ArgIsTypeWithAttrs(self.C, x=23, y='banana')
        self.assertNotEqual(self.C(), eqcb)

    def test_bad_attr_absent(self):
        eqcb = ArgIsTypeWithAttrs(self.C, z='zebra')
        self.assertNotEqual(self.C(), eqcb)
