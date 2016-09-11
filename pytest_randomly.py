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
    out = None

    if config.getoption('randomly_reset_seed'):
        _reseed(config)
        seed = config.getoption('randomly_seed')
        out = "Using --randomly-seed={}".format(seed)

    return out


def pytest_runtest_setup(item):
    if item.config.getoption('randomly_reset_seed'):
        _reseed(item.config)


def pytest_runtest_teardown(item):
    if item.config.getoption('randomly_reset_seed'):
        _reseed(item.config)


def pytest_collection_modifyitems(session, config, items):
    if not config.getoption('randomly_reorganize'):
        return

    if config.getoption('randomly_reset_seed'):
        _reseed(config)

    module_items = []

    current_module = None
    current_items = []
    for item in items:

        if current_module is None:
            current_module = getattr(item, 'module', None)

        if getattr(item, 'module', None) != current_module:
            module_items.append(shuffle_by_class(current_items))
            current_items = [item]
            current_module = item.module
        else:
            current_items.append(item)
    module_items.append(shuffle_by_class(current_items))

    random.shuffle(module_items)

    items[:] = reduce_list_of_lists(module_items)


def shuffle_by_class(items):
    class_items = []
    current_cls = None
    current_items = []

    for item in items:
        if current_cls is None:
            current_cls = getattr(item, 'cls', None)

        if getattr(item, 'cls', None) != current_cls:
            random.shuffle(current_items)
            class_items.append(current_items)
            current_items = [item]
            current_cls = item.cls
        else:
            current_items.append(item)

    random.shuffle(current_items)
    class_items.append(current_items)

    random.shuffle(class_items)

    return reduce_list_of_lists(class_items)


def reduce_list_of_lists(lists):
    new_list = []
    for list_ in lists:
        new_list.extend(list_)
    return new_list
