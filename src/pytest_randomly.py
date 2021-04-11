import argparse
import hashlib
import random

# if sys.version_info < (3, 10):
from importlib_metadata import entry_points
from pytest import Collector, fixture

try:
    import xdist
except ImportError:
    xdist = None

# factory-boy
try:
    from factory.random import set_random_state as factory_set_random_state

    have_factory_boy = True
except ImportError:
    # old versions
    try:
        from factory.fuzzy import set_random_state as factory_set_random_state

        have_factory_boy = True
    except ImportError:
        have_factory_boy = False

# faker
try:
    from faker.generator import random as faker_random

    have_faker = True
except ImportError:
    have_faker = False

# numpy
try:
    from numpy import random as np_random

    have_numpy = True
except ImportError:
    have_numpy = False


default_seed = random.Random().getrandbits(32)


def seed_type(string):
    if string in ("default", "last"):
        return string
    try:
        return int(string)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "{} is not an integer or the string 'last'".format(repr(string))
        )


def pytest_addoption(parser):
    group = parser.getgroup("randomly", "Randomizes tests")
    group._addoption(
        "--randomly-seed",
        action="store",
        dest="randomly_seed",
        default="default",
        type=seed_type,
        help="""Set the seed that pytest-randomly uses (int), or pass the
                special value 'last' to reuse the seed from the previous run.
                Default behaviour: use random.Random().getrandbits(32), so the seed is
                different on each run.""",
    )
    group._addoption(
        "--randomly-dont-reset-seed",
        action="store_false",
        dest="randomly_reset_seed",
        default=True,
        help="""Stop pytest-randomly from resetting random.seed() at the
                start of every test context (e.g. TestCase) and individual
                test.""",
    )
    group._addoption(
        "--randomly-dont-reorganize",
        action="store_false",
        dest="randomly_reorganize",
        default=True,
        help="Stop pytest-randomly from randomly reorganizing the test order.",
    )


def pytest_configure(config):
    if config.pluginmanager.hasplugin("xdist"):
        config.pluginmanager.register(XdistHooks())

    seed_value = config.getoption("randomly_seed")
    if seed_value == "last":
        seed = config.cache.get("randomly_seed", default_seed)
    elif seed_value == "default":
        if hasattr(config, "workerinput"):
            # pytest-xdist: use seed generated on main.
            seed = config.workerinput["randomly_seed"]
        else:
            seed = default_seed
    else:
        seed = seed_value
    config.cache.set("randomly_seed", seed)
    config.option.randomly_seed = seed


class XdistHooks:
    # Hooks for xdist only, registered when needed in pytest_configure()
    # https://docs.pytest.org/en/latest/writing_plugins.html#optionally-using-hooks-from-3rd-party-plugins  # noqa: B950

    def pytest_configure_node(self, node):
        node.workerinput["randomly_seed"] = node.config.getoption("randomly_seed")


random_states = {}
np_random_states = {}


entrypoint_reseeds = None


def _reseed(config, offset=0):
    global entrypoint_reseeds
    seed = config.getoption("randomly_seed") + offset
    if seed not in random_states:
        random.seed(seed)
        random_states[seed] = random.getstate()
    else:
        random.setstate(random_states[seed])

    if have_factory_boy:
        factory_set_random_state(random_states[seed])

    if have_faker:
        faker_random.setstate(random_states[seed])

    if have_numpy:
        numpy_seed = _truncate_seed_for_numpy(seed)
        if numpy_seed not in np_random_states:
            np_random.seed(numpy_seed)
            np_random_states[numpy_seed] = np_random.get_state()
        else:
            np_random.set_state(np_random_states[numpy_seed])

    if entrypoint_reseeds is None:
        entrypoint_reseeds = [
            e.load()
            for e in entry_points().select(group="pytest_randomly.random_seeder")
        ]
    for reseed in entrypoint_reseeds:
        reseed(seed)


def _truncate_seed_for_numpy(seed):
    seed = abs(seed)
    if seed <= 2 ** 32 - 1:
        return seed

    seed_bytes = seed.to_bytes(seed.bit_length(), "big")
    return int.from_bytes(hashlib.sha512(seed_bytes).digest()[: 32 // 8], "big")


def pytest_report_header(config):
    seed = config.getoption("randomly_seed")
    _reseed(config)
    return "Using --randomly-seed={}".format(seed)


def pytest_runtest_setup(item):
    if item.config.getoption("randomly_reset_seed"):
        _reseed(item.config, -1)


def pytest_runtest_call(item):
    if item.config.getoption("randomly_reset_seed"):
        _reseed(item.config)


def pytest_runtest_teardown(item):
    if item.config.getoption("randomly_reset_seed"):
        _reseed(item.config, 1)


def pytest_collection_modifyitems(config, items):
    if not config.getoption("randomly_reorganize"):
        return

    _reseed(config)

    module_items = []

    current_module = None
    current_items = []
    for item in items:

        try:
            item_module = getattr(item, "module", None)
        except (ImportError, Collector.CollectError):
            item_module = None

        if current_module is None:
            current_module = item_module

        if item_module != current_module:
            module_items.append(shuffle_by_class(current_items))
            current_items = [item]
            current_module = item_module
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
            current_cls = getattr(item, "cls", None)

        if getattr(item, "cls", None) != current_cls:
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


if have_faker:

    @fixture(autouse=True)
    def faker_seed(pytestconfig):
        return pytestconfig.getoption("randomly_seed")
