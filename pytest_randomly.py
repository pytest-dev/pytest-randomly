# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import random
import time
from collections import defaultdict

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
        dest='randomly_reset_seed', default=True,
        help="""Stop pytest-randomly from resetting random.seed() at the
                start of every test context (e.g. TestCase) and individual
                test."""
    )
    group._addoption(
        '--randomly-dont-reorganize', action='store_false',
        dest='randomly_reorganize', default=True,
        help="Stop pytest-randomly from randomly reorganizing the test order."
    )


random_states = {}


def _reseed(config):
    seed = config.getoption('randomly_seed')
    if seed not in random_states:
        random.seed(seed)
        random_states[seed] = random.getstate()
    else:
        random.setstate(random_states[seed])

    if have_factory_boy:
        factory_set_random_state(random_states[seed])

    if have_faker:
        faker_random.setstate(random_states[seed])


def pytest_report_header(config):
    if not config.getoption('with_randomly'):
        return

    out = None

    if config.getoption('randomly_reset_seed'):
        _reseed(config)
        seed = config.getoption('randomly_seed')
        out = "Using --randomly-seed={}".format(seed)

    return out


def pytest_runtest_setup(item):
    if not item.config.getoption('with_randomly'):
        return

    if item.config.getoption('randomly_reset_seed'):
        _reseed(item.config)


def pytest_collection_modifyitems(session, config, items):
    if not config.getoption('with_randomly'):
        return

    if not config.getoption('randomly_reorganize'):
        return

    if config.getoption('randomly_reset_seed'):
        _reseed(config)

    modules = []
    grouped_items = defaultdict(lambda: defaultdict(list))  # module then class
    for item in items:
        grouped_items[item.module][item.cls].append(item)
        if not modules or modules[-1] != item.module:
            modules.append(item.module)

    new_items = []
    random.shuffle(modules)
    for module in modules:
        module_items = grouped_items[module]
        module_classes = list(grouped_items[module].keys())
        random.shuffle(module_classes)

        for cls in module_classes:
            cls_items = module_items[cls]
            random.shuffle(cls_items)
            new_items.extend(cls_items)

    items[:] = new_items
