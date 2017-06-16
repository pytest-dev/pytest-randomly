.. :changelog:

History
-------

Pending Release
---------------

* New release notes here

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
