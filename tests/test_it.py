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

        gnum = None

        def test_a():
            global gnum
            lnum = random.random()
            if gnum is None:
                gnum = lnum
            else:
                assert lnum == gnum

        def test_b():
            global gnum
            lnum = random.random()
            if gnum is None:
                gnum = lnum
            else:
                assert lnum == gnum
        """
    )
    out = testdir.runpytest('--with-randomly')
    out.assert_outcomes(passed=2, failed=0)
