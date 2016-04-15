# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import six

if six.PY3:
    pytest_plugins = ['pytester']
else:
    pytest_plugins = [b'pytester']


@pytest.fixture
def simpletestdir(testdir):
    testdir.makepyfile(
        test_one="""
        def test_a():
            assert True
        """
    )
    return testdir


def test_it_reports_a_header_when_not_set(simpletestdir):
    out = simpletestdir.runpytest()
    assert len([
        x for x in out.outlines if x.startswith('Using --randomly-seed=')
    ]) == 1


def test_it_reports_a_header_when_set(simpletestdir):
    out = simpletestdir.runpytest('--randomly-seed=10')
    lines = [x for x in out.outlines if x.startswith('Using --randomly-seed=')]
    assert lines == [
        'Using --randomly-seed=10'
    ]


def test_it_reuses_the_same_random_seed_per_test(testdir):
    testdir.makepyfile(
        test_one="""
        import random

        def test_a():
            test_a.num = random.random()
            if hasattr(test_b, 'num'):
                assert test_a.num == test_b.num

        def test_b():
            test_b.num = random.random()
            if hasattr(test_a, 'num'):
                assert test_b.num == test_a.num
        """
    )
    out = testdir.runpytest('--randomly-dont-reorganize')
    out.assert_outcomes(passed=2, failed=0)


def test_it_resets_the_random_seed_at_the_start_of_test_classes(testdir):
    testdir.makepyfile(
        test_one="""
        import random
        from unittest import TestCase


        class A(TestCase):
            @classmethod
            def setUpClass(cls):
                super(A, cls).setUpClass()
                cls.suc_num = random.random()

            def test_it(self):
                test_num = random.random()
                assert self.suc_num == test_num

            def test_it2(self):
                test_num = random.random()
                assert self.suc_num == test_num

            @classmethod
            def tearDownClass(cls):
                assert random.random() == cls.suc_num
                super(A, cls).tearDownClass()
        """
    )
    out = testdir.runpytest('--randomly-dont-reorganize')
    out.assert_outcomes(passed=2, failed=0)


def test_the_same_random_seed_per_test_can_be_turned_off(testdir):
    testdir.makepyfile(
        test_one="""
        import random

        def test_a():
            test_a.state1 = random.getstate()
            assert test_a.state1 == random.getstate()  # sanity check
            assert random.random() >= 0  # mutate state
            test_a.state2 = random.getstate()

        def test_b():
            test_b.state = random.getstate()
            assert test_b.state == random.getstate()  # sanity check
            assert test_a.state1 != test_b.state
            assert test_a.state2 == test_b.state
        """
    )
    out = testdir.runpytest(
        '--randomly-dont-reset-seed', '--randomly-dont-reorganize',
    )
    out.assert_outcomes(passed=2, failed=0)


def test_files_reordered(testdir):
    code = """
        def test_it():
            pass
    """
    testdir.makepyfile(
        test_a=code,
        test_b=code,
        test_c=code,
        test_d=code,
    )
    args = ['-v']
    if six.PY3:  # Python 3 random changes
        args.append('--randomly-seed=15')
    else:
        args.append('--randomly-seed=41')

    out = testdir.runpytest(*args)

    out.assert_outcomes(passed=4, failed=0)
    assert out.outlines[8:12] == [
        'test_d.py::test_it PASSED',
        'test_c.py::test_it PASSED',
        'test_a.py::test_it PASSED',
        'test_b.py::test_it PASSED',
    ]


def test_classes_reordered(testdir):
    testdir.makepyfile(
        test_one="""
        from unittest import TestCase


        class A(TestCase):
            def test_a(self):
                pass


        class B(TestCase):
            def test_b(self):
                pass


        class C(TestCase):
            def test_c(self):
                pass


        class D(TestCase):
            def test_d(self):
                pass
        """
    )
    args = ['-v']
    if six.PY3:  # Python 3 random changes
        args.append('--randomly-seed=15')
    else:
        args.append('--randomly-seed=41')

    out = testdir.runpytest(*args)

    out.assert_outcomes(passed=4, failed=0)
    assert out.outlines[8:12] == [
        'test_one.py::D::test_d PASSED',
        'test_one.py::C::test_c PASSED',
        'test_one.py::A::test_a PASSED',
        'test_one.py::B::test_b PASSED',
    ]


def test_class_test_methods_reordered(testdir):
    testdir.makepyfile(
        test_one="""
        from unittest import TestCase

        class T(TestCase):
            def test_a(self):
                pass

            def test_b(self):
                pass

            def test_c(self):
                pass

            def test_d(self):
                pass
        """
    )
    args = ['-v']
    if six.PY3:  # Python 3 random changes
        args.append('--randomly-seed=15')
    else:
        args.append('--randomly-seed=41')

    out = testdir.runpytest(*args)

    out.assert_outcomes(passed=4, failed=0)
    assert out.outlines[8:12] == [
        'test_one.py::T::test_d PASSED',
        'test_one.py::T::test_c PASSED',
        'test_one.py::T::test_a PASSED',
        'test_one.py::T::test_b PASSED',
    ]


def test_doctests_reordered(testdir):
    testdir.makepyfile(
        test_one="""
        def foo():
            '''
            >>> foo()
            9001
            '''
            return 9001

        def bar():
            '''
            >>> bar()
            9002
            '''
            return 9002
        """
    )
    args = ['-v', '--doctest-modules']
    if six.PY3:  # Python 3 random changes
        args.append('--randomly-seed=5')
    else:
        args.append('--randomly-seed=2')

    out = testdir.runpytest(*args)
    out.assert_outcomes(passed=2)
    assert out.outlines[8:10] == [
        'test_one.py::test_one.bar PASSED',
        'test_one.py::test_one.foo PASSED',
    ]
