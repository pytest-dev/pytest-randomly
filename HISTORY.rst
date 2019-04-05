.. :changelog:

History
-------

Pending Release
---------------

.. Insert new release notes below this line

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
