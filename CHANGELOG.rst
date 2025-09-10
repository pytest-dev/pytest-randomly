=========
Changelog
=========

4.0.0 (2025-09-10)
------------------

* Support Python 3.14.

* Use a different random seed per test, based on the test ID.

  This change should mean that tests exercise more random data values in a given run, and that any randomly-generated identifiers have a lower chance of collision when stored in a shared resource like a database.

  `PR #687 <https://github.com/pytest-dev/pytest-randomly/issues/687>`__.
  Thanks to Bryce Drennan for the suggestion in `Issue #600 <https://github.com/pytest-dev/pytest-randomly/issues/600>`__ and initial implementation in `PR #617 <https://github.com/pytest-dev/pytest-randomly/pull/617>`__.

* Move from MD5 to CRC32 for hashing test IDs, as it’s 5x faster and we don’t need cryptographic security.

  `Issue #686 <https://github.com/pytest-dev/pytest-randomly/issues/686>`__.

3.16.0 (2024-10-25)
-------------------

* Drop Python 3.8 support.

* Support Python 3.13.

3.15.0 (2023-08-15)
-------------------

* Support Python 3.12.

3.14.0 (2023-08-15)
-------------------

* Reset the random state for `Model Bakery <https://model-bakery.readthedocs.io/en/latest/>`__.

3.13.0 (2023-07-10)
-------------------

* Drop Python 3.7 support.

3.12.0 (2022-05-11)
-------------------

* Support Python 3.11.

3.11.0 (2022-01-10)
-------------------

* Drop Python 3.6 support.

3.10.3 (2021-11-30)
-------------------

* Work on FIPS Python 3.9+, by declaring use of ``hashlib.md5()`` as not used for security.

  Thanks to dantebben for the report in `Issue #414 <https://github.com/pytest-dev/pytest-randomly/issues/414>`__.

3.10.2 (2021-11-10)
-------------------

* Fix crash when pytest’s cacheprovider is disabled.

  Thanks to Mandeep Sandhu for the report in `Issue #408
  <https://github.com/pytest-dev/pytest-randomly/issues/408>`__.

* Improve group name in ``pytest --help``.

3.10.1 (2021-08-13)
-------------------

* Fix new shuffling to work when one or more test in a class or module have the
  same test id.

  Thanks to Nikita Sobolev for the report in `Issue #378
  <https://github.com/pytest-dev/pytest-randomly/issues/378>`__.

3.10.0 (2021-08-13)
-------------------

* Rework shuffling algorithm to use hashing. This means that running a subset
  of tests with the same seed will now produce the same ordering as running the
  full set of tests. This allows narrowing down ordering-related failures.

  Thanks to Tom Grainger for the suggestion in `Issue #210
  <https://github.com/pytest-dev/pytest-randomly/issues/210>`__.

* Shuffle before other test collection hooks. This allows
  pytest’s `--stepwise flag
  <https://docs.pytest.org/en/latest/cache.html#stepwise>`__ to work, among
  other things.

  Thanks to Tom Grainger for the suggestion to try with ``--stepwise``. Fixes
  `Issue #376
  <https://github.com/pytest-dev/pytest-randomly/issues/376>`__.

3.9.0 (2021-08-12)
------------------

* Add type hints.

3.8.0 (2021-05-10)
------------------

* Support Python 3.10.

3.7.0 (2021-04-11)
------------------

* Drop dependency on ``backports.entry-points-selectable`` by depending on
  ``importlib-metadata`` version 3.6.0+.

3.6.0 (2021-04-01)
------------------

* Fix deprecation warning from importlib-metadata 3.9.0+.

  Thanks to Dominic Davis-Foster for report in `Issue #333
  <https://github.com/pytest-dev/pytest-randomly/issues/333>`__.

* Stop distributing tests to reduce package size. Tests are not intended to be
  run outside of the tox setup in the repository. Repackagers can use GitHub's
  tarballs per tag.

* Drop Python 3.5 support.

3.5.0 (2020-11-16)
------------------

* Support Python 3.9.
* Move license from BSD to MIT License.

3.4.1 (2020-07-10)
------------------

* Fix numpy error ``ValueError: Seed must be between 0 and 2**32 - 1`` when
  passed a seed outside of this range.

3.4.0 (2020-05-27)
------------------

* Provide a ``faker_seed`` fixture to set the seed for tests using faker's
  pytest fixtures (as per its
  `docs <https://faker.readthedocs.io/en/master/pytest-fixtures.html#seeding-configuration>`__).

  Thanks to Romain Létendart for the change in `PR #261
  <https://github.com/pytest-dev/pytest-randomly/pull/261>`__.

3.3.1 (2020-04-15)
------------------

* Fix to work when pytest-xdist is not installed or active
  (``PluginValidationError: unknown hook 'pytest_configure_node'``).

3.3.0 (2020-04-15)
------------------

* Add `pytest-xdist <https://pypi.org/project/pytest-xdist/>`__ support.
  Previously it only worked reliably when setting ``--randomly-seed``
  explicitly. When not provided, the default seed generated in workers could
  differ and collection would fail. Now when it is not provided, all xdist
  worker processes shared the same default seed generated in the main
  process.

3.2.1 (2020-01-13)
------------------

* Update ``MANIFEST.in`` so tests are included in the sdist tarball again.

3.2.0 (2019-12-19)
------------------

* Converted setuptools metadata to configuration file. This meant removing the
  ``__version__`` attribute from the package. If you want to inspect the
  installed version, use
  ``importlib.metadata.version("pytest-randomly")``
  (`docs <https://docs.python.org/3.8/library/importlib.metadata.html#distribution-versions>`__ /
  `backport <https://pypi.org/project/importlib-metadata/>`__).
* Convert reading entrypoints to use ``importlib.metadata``. Depend on
  ``importlib-metadata`` on Python < 3.8.
* Update Python support to 3.5-3.8.

3.1.0 (2019-08-25)
------------------

* Add plugins via entry points ``pytest_randomly.random_seeder`` to allow
  outside packages to register additional random generators to seed. This has
  added a dependency on the ``entrypoints`` package.

3.0.0 (2019-04-05)
------------------

* Update Python support to 3.5-3.7, as 3.4 has reached its end of life.
* Handle ``CollectError``\s and ``ImportError``\s during collection when
  accessing ``item.module``.

2.1.1 (2019-03-26)
------------------

* Fix including tests in sdist after re-arrangement in 2.1.0.

2.1.0 (2019-03-01)
------------------

* Add the option ``--randomly-seed=last`` to reuse the last used value for the
  seed.

2.0.0 (2019-02-28)
------------------

* Drop Python 2 support, only Python 3.4+ is supported now.

1.2.3 (2017-12-06)
------------------

* Fix ``DeprecationWarning`` with recent versions of ``factory_boy``.

1.2.2 (2017-11-03)
------------------

* Fix collection to not sometimes crash when encountering pytest ``Item``\s
  without a module.

1.2.1 (2017-06-17)
------------------

* Fix collection to be deterministically shuffled again, regression in 1.2.0.

1.2.0 (2017-06-16)
------------------

* Dropped Python 2.6 compatibility, as upstream dependency NumPy did.
* Reset and output the seed at the start of the test run when
  ``--randomly-dont-reset-seed`` is set, to allow the reorganization of tests
  to be reproducible.

1.1.2 (2016-10-27)
------------------

* Reset the random state for NumPy too.

1.1.1 (2016-09-16)
------------------

* Add Python 2.6 compatibility

1.1.0 (2016-09-12)
------------------

* Offset the random seed during test setup and teardown. This is to avoid the
  awkward situation where test setup generates a random object, then the test
  generates a second one, but due to the re-seeding, they end up being always
  the same object. Thanks @rouge8 for the report.

1.0.0 (2016-04-15)
------------------

* First release on PyPI.
