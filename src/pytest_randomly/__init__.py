import argparse
import hashlib
import random
import sys
from itertools import groupby
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item
from pytest import Collector, fixture, hookimpl

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

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


def seed_type(string: str) -> Union[str, int]:
    if string in ("default", "last"):
        return string
    try:
        return int(string)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{repr(string)} is not an integer or the string 'last'"
        )


def pytest_addoption(parser: Parser) -> None:
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


def pytest_configure(config: Config) -> None:
    if config.pluginmanager.hasplugin("xdist"):
        config.pluginmanager.register(XdistHooks())

    seed_value = config.getoption("randomly_seed")
    if seed_value == "last":
        assert config.cache is not None
        seed = config.cache.get("randomly_seed", default_seed)
    elif seed_value == "default":
        if hasattr(config, "workerinput"):
            # pytest-xdist: use seed generated on main.
            seed = config.workerinput["randomly_seed"]  # type: ignore [attr-defined]
        else:
            seed = default_seed
    else:
        seed = seed_value
    assert config.cache is not None
    config.cache.set("randomly_seed", seed)
    config.option.randomly_seed = seed


class XdistHooks:
    # Hooks for xdist only, registered when needed in pytest_configure()
    # https://docs.pytest.org/en/latest/writing_plugins.html#optionally-using-hooks-from-3rd-party-plugins  # noqa: B950

    def pytest_configure_node(self, node: Item) -> None:
        seed = node.config.getoption("randomly_seed")
        node.workerinput["randomly_seed"] = seed  # type: ignore [attr-defined]


random_states: Dict[int, object] = {}
np_random_states: Dict[int, Any] = {}


entrypoint_reseeds: Optional[List[Callable[[int], None]]] = None


def _reseed(config: Config, offset: int = 0) -> int:
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
            e.load() for e in entry_points(group="pytest_randomly.random_seeder")
        ]
    for reseed in entrypoint_reseeds:
        reseed(seed)

    return seed


def _truncate_seed_for_numpy(seed: int) -> int:
    seed = abs(seed)
    if seed <= 2 ** 32 - 1:
        return seed

    seed_bytes = seed.to_bytes(seed.bit_length(), "big")
    return int.from_bytes(hashlib.sha512(seed_bytes).digest()[: 32 // 8], "big")


def pytest_report_header(config: Config) -> str:
    seed = config.getoption("randomly_seed")
    _reseed(config)
    return f"Using --randomly-seed={seed}"


def pytest_runtest_setup(item: Item) -> None:
    if item.config.getoption("randomly_reset_seed"):
        _reseed(item.config, -1)


def pytest_runtest_call(item: Item) -> None:
    if item.config.getoption("randomly_reset_seed"):
        _reseed(item.config)


def pytest_runtest_teardown(item: Item) -> None:
    if item.config.getoption("randomly_reset_seed"):
        _reseed(item.config, 1)


@hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: Config, items: List[Item]) -> None:
    if not config.getoption("randomly_reorganize"):
        return

    seed = _reseed(config)

    modules_items: List[Tuple[Optional[ModuleType], List[Item]]] = []
    for module, group in groupby(items, _get_module):
        modules_items.append(
            (
                module,
                _shuffle_by_class(list(group), seed),
            )
        )

    def _module_key(module_item: Tuple[Optional[ModuleType], List[Item]]) -> bytes:
        module, _items = module_item
        if module is None:
            return _md5(f"{seed}::None")
        return _md5(f"{seed}::{module.__name__}")

    modules_items.sort(key=_module_key)

    items[:] = reduce_list_of_lists([subitems for module, subitems in modules_items])


def _get_module(item: Item) -> Optional[ModuleType]:
    try:
        return getattr(item, "module", None)
    except (ImportError, Collector.CollectError):
        return None


def _shuffle_by_class(items: List[Item], seed: int) -> List[Item]:
    klasses_items: List[Tuple[Optional[Type[Any]], List[Item]]] = []

    for klass, group in groupby(items, _get_cls):
        klass_items = [(_md5(f"{seed}::{item.nodeid}"), item) for item in group]
        klass_items.sort()
        klasses_items.append(
            (
                klass,
                [item for _key, item in klass_items],
            )
        )

    def _cls_key(klass_items: Tuple[Optional[Type[Any]], List[Item]]) -> bytes:
        klass, items = klass_items
        if klass is None:
            return _md5(f"{seed}::None")
        return _md5(f"{seed}::{klass.__module__}.{klass.__qualname__}")

    klasses_items.sort(key=_cls_key)

    return reduce_list_of_lists([subitems for klass, subitems in klasses_items])


def _get_cls(item: Item) -> Optional[Type[Any]]:
    return getattr(item, "cls", None)


T = TypeVar("T")


def reduce_list_of_lists(lists: List[List[T]]) -> List[T]:
    new_list = []
    for list_ in lists:
        new_list.extend(list_)
    return new_list


def _md5(string: str) -> bytes:
    hasher = hashlib.md5()
    hasher.update(string.encode())
    return hasher.digest()


if have_faker:

    @fixture(autouse=True)
    def faker_seed(pytestconfig: Config) -> None:
        return pytestconfig.getoption("randomly_seed")
