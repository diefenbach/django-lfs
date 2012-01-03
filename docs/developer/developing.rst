.. index:: Developing LFS

==============
Developing LFS
==============

This section describes how to develop LFS.

Creating a Development Environment
===================================

There is an installer based on `zc.buildout <http://www.buildout.org/>`_, which
should make the installation straightforward:

#. $ hg cl https://bitbucket.org/diefenbach/lfs-buildout-development

#. $ cd lfs-buildout-development

#. $ python bootstrap.py

#. $ bin/buildout -v

#. $ bin/django syncdb

#. $ bin/django lfs_init

#. $ bin/django test lfs.core

.. note::

  You might want to fork LFS on `Bitbucket <https://bitbucket.org/diefenbach
  /django-lfs>`_ or `GitHub <https://github.com/diefenbach/django-lfs>`_ and
  point to it within buildout.cfg first.

Contributing Code to the Core
=============================

If you consider to contribute code to LFS, please read the following statements.

* First of all, you are very welcome!

* Generally, it would be great if you would discuss new stuff first. We are very
  reluctant to add new things. Every new feature should have a real live use
  case.

* Your code must be put under a `permissive free software license
  <http://en.wikipedia.org/wiki/BSD_licenses>`_ like BSD, otherwise we can't add
  it. For instance, code under the GPL or a other `copyleft software licenses
  <http://en.wikipedia.org/wiki/copyleft>`_ won't be added to the core.

* Fork LFS on `Bitbucket <https://bitbucket.org/diefenbach/django-lfs>`_ or
  `GitHub <https://github.com/diefenbach/django-lfs>`_ and send us pull
  requests. If you fix a bug or implement a new feature, please make sure that
  you just add related code to your repository. This makes it easier to review
  and pull your code.

* Python code must follow `PEP 8 <http://www.python.org/dev/peps/pep-0008/>`_.
  The maximum of 79 characters per line is the only exception. You may want to
  check your code with `pep8 <http://pypi.python.org/pypi/pep8/>`_. The
  following statement should run without complaints::

    $ pep8 --repeat --ignore=E501 /path/to/lfs

* Every new feature must have unit tests and documentation. Without one of those
  it must be very interesting in order to be added :-)

* All tests must pass. Please check this with (see :doc:`testing`)::

   $ bin/django test lfs.core

* New features shouldn't make LFS slower. Please see :doc:`benchmarking`.

Contributing Translations
=========================

Please refer to :doc:`/misc/contributing_translations`.
