.. :changelog:

History
-------

Pending Release
---------------

* Add support for python2.6

1.1.0 (2016-09-12)
------------------

* Offset the random seed during test setup and teardown. This is to avoid the
  awkward situation where test setup generates a random object, then the test
  generates a second one, but due to the re-seeding, they end up being always
  the same object. Thanks @rouge8 for the report.

1.0.0 (2016-04-15)
------------------

* First release on PyPI.
