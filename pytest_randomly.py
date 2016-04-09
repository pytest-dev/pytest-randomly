# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import random
import time

# factory-boy
try:
    from factory.fuzzy import set_random_state as factory_set_random_state
    have_factory_boy = True
except ImportError:
    have_factory_boy = False

# fake-factory
try:
    from faker.generator import random as faker_random
    have_faker = True
except ImportError:
    have_faker = False


__version__ = '1.0.0'


def pytest_addoption(parser):
    group = parser.getgroup('randomly', 'Randomizes tests')
    group._addoption(
        '--with-randomly', action='store_true', dest='with_randomly',
        default=False,
        help="""Activates pytest-randomly to randomize the tests, in order and
                random.seed(). Defaults to False."""
    )
    group._addoption(
        '--randomly-seed', action='store', dest='randomly_seed',
        default=int(time.time()), type=int,
        help="""Set the seed that pytest-randomly uses. Default behaviour:
                use time.time()"""
    )
    group._addoption(
        '--randomly-dont-reset-seed', action='store_false',
        dest='reset_seed', default=True,
        help="""Stop pytest-randomly from resetting random.seed() at the
                start of every test context (e.g. TestCase) and individual
                test."""
    )


activated = False
seed = None
reset_seed = None
random_state = None


def _reseed():
    global random_state
    if random_state is None:
        random.seed(seed)
        random_state = random.getstate()
    else:
        random.setstate(random_state)

    if have_factory_boy:
        factory_set_random_state(random_state)

    if have_faker:
        faker_random.setstate(random_state)


def pytest_report_header(config):
    global activated, reset_seed, seed
    out = None

    if not config.getoption('with_randomly'):
        return
    activated = True

    seed = config.getoption('randomly_seed')

    reset_seed = config.getoption('reset_seed')

    if reset_seed:
        _reseed()
        out = "Using --randomly-seed={}".format(seed)

    return out


def pytest_runtest_setup(item):
    if not activated:
        return

    if reset_seed:
        _reseed()
