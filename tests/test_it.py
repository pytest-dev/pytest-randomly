# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import six
import sys

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
    out = simpletestdir.runpytest('--with-randomly')
    assert len([
        x for x in out.outlines if x.startswith('Using --randomly-seed=')
    ]) == 1


def test_it_reports_a_header_when_set(simpletestdir):
    out = simpletestdir.runpytest('--with-randomly', '--randomly-seed=10')
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
    out = testdir.runpytest('--with-randomly')
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
        '-v',
        '--with-randomly', '--randomly-dont-reset-seed',
        # '--randomly-dont-shuffle-modules', '--randomly-dont-shuffle-cases',
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
    args = ['-v', '--with-randomly']
    if sys.version_info >= (3, 0):  # Python 3 random changes
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

    print(out)
    assert 0
