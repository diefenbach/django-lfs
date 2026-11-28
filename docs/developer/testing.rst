.. index:: Testing LFS

===========
Testing LFS
===========

This section describes how to run the tests of LFS. Set up the checkout first, see :doc:`developing`.

Overview
========

The tests use `pytest <https://docs.pytest.org/>`_ with `pytest-django <https://pytest-django.readthedocs.io/>`_.
``uv sync`` installs them. The tests run against the settings in ``tests/settings.py``: LFS with the default theme,
SQLite in memory, and no optional add-ons. Tests of features that need an add-on (for instance lfs-paypal or
lfs-gtm) skip themselves when the add-on is not installed; they are marked with
``lfs.tests.utils.requires_addon``.

Examples
========

Test everything, on all CPU cores::

    $ uv run pytest -n auto

Test only the catalog::

    $ uv run pytest lfs/catalog

Test only one test, without capturing the output (helpful to debug it with ``breakpoint()``)::

    $ uv run pytest lfs/catalog/tests.py::ViewsTestCase::test_file -s

Show the slowest tests::

    $ uv run pytest -n auto --durations=10

.. note::

    The test suite of LFS 1.0 is not fully green yet: about 80 tests fail and about 25 tests have errors, also on
    ``main``. Make sure your change adds no new failures: run the tests before and after your change and compare.

See also
========

* `pytest <https://docs.pytest.org/>`_
* `pytest-django <https://pytest-django.readthedocs.io/>`_
* `pytest-xdist <https://pytest-xdist.readthedocs.io/>`_ (``-n auto``)
