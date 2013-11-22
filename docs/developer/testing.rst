.. index:: Testing LFS

===========
Testing LFS
===========

This section describes how to test LFS.

Overview
========

Testing is based on `nose <http://readthedocs.org/docs/nose/en/latest/>`_ and
`django-nose <http://pypi.python.org/pypi/django-nose>`_.

Examples
========

Test everything::

    $ bin/django test lfs.core

Test everything with coverage (you'll find the coverage report in the current
directory)::

    $ bin/django test lfs.core --with-coverage --cover-package=lfs --cover-html

Test only the catalog::

    $ bin/django test lfs.catalog

Test only the catalog with coverage (you'll find the coverage report in the
current directory)::

    $ bin/django test lfs.catalog --with-coverage --cover-package=lfs.catalog --cover-html

Test only one method without capturing the output (this is helpful if you want
to debug a test with pdb)::

    $ bin/django test lfs.catalog.tests:ViewsTestCase.test_file -s

See also
========

* `nose <http://readthedocs.org/docs/nose/en/latest/>`_
* `nose options <http://readthedocs.org/docs/nose/en/latest/usage.html#options>`_
* `django-nose <http://pypi.python.org/pypi/django-nose>`_
