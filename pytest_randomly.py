# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import random
import time

__version__ = '1.0.0'


def pytest_addoption(parser):
    group = parser.getgroup('randomly', 'Randomizes tests')
    group._addoption(
        '--with-randomly', action='store_true', dest='with_randomly',
        default=False, help='Randomizes the tests. Defaults to False.'
    )
    group._addoption(
        '--randomly-seed', action='store', dest='randomly_seed',
        default=int(time.time()), type=int,
        help="""Set the seed that nose-randomly uses. Default behaviour:
                use time.time()"""
    )

seed = None


def pytest_report_header(config):
    global seed
    if config.option.with_randomly:
        seed = config.option.randomly_seed
        random.seed(seed)
        return "Using --randomly-seed={}".format(seed)


def pytest_runtest_setup(item):
    global seed
    random.seed(seed)
