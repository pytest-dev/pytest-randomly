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
                assert cls.suc_num == getattr(B, 'suc_num', cls.suc_num)

            def test_fake(self):
                assert True


        class B(TestCase):

            @classmethod
            def setUpClass(cls):
                super(B, cls).setUpClass()
                cls.suc_num = random.random()
                assert cls.suc_num == getattr(A, 'suc_num', cls.suc_num)

            def test_fake(self):
                assert True
        """
    )
    out = testdir.runpytest()
    out.assert_outcomes(passed=2, failed=0)


def test_it_resets_the_random_seed_at_the_end_of_test_classes(testdir):
    testdir.makepyfile(
        test_one="""
        import random
        from unittest import TestCase


        class A(TestCase):

            def test_fake(self):
                assert True

            @classmethod
            def tearDownClass(cls):
                super(A, cls).tearDownClass()
                cls.suc_num = random.random()
                assert cls.suc_num == getattr(B, 'suc_num', cls.suc_num)


        class B(TestCase):

            def test_fake(self):
                assert True

            @classmethod
            def tearDownClass(cls):
                super(B, cls).tearDownClass()
                cls.suc_num = random.random()
                assert cls.suc_num == getattr(A, 'suc_num', cls.suc_num)
        """
    )
    out = testdir.runpytest()
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


def test_files_reordered_when_seed_not_reset(testdir):
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

    args.append('--randomly-dont-reset-seed')
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


def test_doctests_in_txt_files_reordered(testdir):
    testdir.tmpdir.join('test.txt').write('''\
        >>> 2 + 2
        4
        ''')
    testdir.tmpdir.join('test2.txt').write('''\
        >>> 2 - 2
        0
        ''')
    args = ['-v']
    if six.PY3:  # Python 3 random changes
        args.append('--randomly-seed=1')
    else:
        args.append('--randomly-seed=4')

    out = testdir.runpytest(*args)
    out.assert_outcomes(passed=2)
    assert out.outlines[8:10] == [
        'test2.txt::test2.txt PASSED',
        'test.txt::test.txt PASSED',
    ]


def test_fixtures_get_different_random_state_to_tests(testdir):
    testdir.makepyfile(
        test_one="""
        import random

        import pytest


        @pytest.fixture()
        def myfixture():
            return random.getstate()


        def test_one(myfixture):
            assert myfixture != random.getstate()
        """
    )
    out = testdir.runpytest()
    out.assert_outcomes(passed=1)


def test_fixtures_dont_interfere_with_tests_getting_same_random_state(testdir):
    testdir.makepyfile(
        test_one="""
        import random

        import pytest


        random.seed(2)
        state_at_seed_two = random.getstate()


        @pytest.fixture(scope='module')
        def myfixture():
            return random.random()


        @pytest.mark.one()
        def test_one(myfixture):
            assert random.getstate() == state_at_seed_two


        @pytest.mark.two()
        def test_two(myfixture):
            assert random.getstate() == state_at_seed_two
        """
    )
    args = ['--randomly-seed=2']

    out = testdir.runpytest(*args)
    out.assert_outcomes(passed=2)

    out = testdir.runpytest('-m', 'one', *args)
    out.assert_outcomes(passed=1)
    out = testdir.runpytest('-m', 'two', *args)
    out.assert_outcomes(passed=1)


def test_numpy(testdir):
    testdir.makepyfile(
        test_one="""
        import numpy as np

        def test_one():
            assert np.random.rand() == 0.417022004702574

        def test_two():
            assert np.random.rand() == 0.417022004702574
        """
    )

    out = testdir.runpytest('--randomly-seed=1')
    out.assert_outcomes(passed=2)


def test_faker(testdir):
    testdir.makepyfile(
        test_one="""
        from faker import Faker

        fake = Faker()

        def test_one():
            assert fake.name() == 'Ryan Gallagher'

        def test_two():
            assert fake.name() == 'Ryan Gallagher'
        """
    )

    out = testdir.runpytest('--randomly-seed=1')
    out.assert_outcomes(passed=2)
