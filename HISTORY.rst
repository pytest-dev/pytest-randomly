-------
History
-------

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
  worker processes shared the same default seed generated in the master
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

* Fix collection to not sometimes crash when encoutering pytest ``Item``\s
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
