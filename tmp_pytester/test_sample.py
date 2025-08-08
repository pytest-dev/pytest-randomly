from __future__ import annotations

from unittest import mock

import pytest_randomly


class _FakeEntryPoint:
    def __init__(self, name: str, obj: mock.Mock):
        self.name = name
        self._obj = obj

    def load(self):
        print("load called for", self.name)
        return self._obj


def test_run(pytester):
    (pytester.path / "test_one.py").write_text("def test_one(): pass\n")
    entry_points = []

    def fake_entry_points(*, group):
        print("fake entry_points called with group", group)
        return entry_points

    pytest_randomly.entrypoint_reseeds = None
    pytest_randomly.entry_points = fake_entry_points
    reseed = mock.Mock()
    entry_points.append(_FakeEntryPoint("test", reseed))
    result = pytester.runpytest_inprocess("--randomly-seed=1")
    print("mock calls", reseed.mock_calls)
    assert result.ret == 0
