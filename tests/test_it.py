# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import six

if six.PY3:
    pytest_plugins = ['pytester']
else:
    pytest_plugins = [b'pytester']


@pytest.fixture
def rtestdir(testdir):
    testdir.tmpdir.ensure("__init__.py")
    testdir.makepyfile(
        test_one="""
        def test_a():
            assert True
        """
    )
    return testdir


def test_it_reports_a_header_when_not_set(rtestdir):
    out = rtestdir.runpytest('--with-randomly')
    assert len([
        x for x in out.outlines if x.startswith('Using --randomly-seed=')
    ]) == 1


def test_it_reports_a_header_when_set(rtestdir):
    out = rtestdir.runpytest('--with-randomly', '--randomly-seed=10')
    lines = [x for x in out.outlines if x.startswith('Using --randomly-seed=')]
    assert lines == [
        'Using --randomly-seed=10'
    ]
