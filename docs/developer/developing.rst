.. index:: Developing LFS

==============
Developing LFS
==============

This section describes how to develop LFS.

.. warning::

  This is only for development. Don't use this version in production. We might
  break the head, add stuff which need database migrations or introduce some
  security issues, etc.

Creating a Development Environment
===================================

There is an installer based on `zc.buildout <http://www.buildout.org/>`_, which
should make the installation straightforward:

#. $ git clone https://github.com/diefenbach/lfs-buildout-development.git

#. $ cd lfs-buildout-development

#. $ python bootstrap.py

#. $ bin/buildout -v

#. $ bin/django syncdb

#. $ bin/django migrate

#. $ bin/django lfs_init

#. $ bin/django test lfs.core

#. $ bin/django runserver

#. Browse to http://localhost:8000

.. note::

  You might want to fork LFS on `GitHub <https://github.com/diefenbach/django-lfs>`_
  and point to it within buildout.cfg first.

Contributing Code to the Core
=============================

If you consider to contribute code to LFS, please read the following statements
first:

#. First of all, you are very welcome!

#. Generally, it would be great if you would discuss new stuff first. We are
   very reluctant to add new things. Every new feature should have a real live
   use case. Find us on `IRC <irc://irc.freenode.net/django-lfs>`_ or the
   `LFS Google Group <http://groups.google.com/group/django-lfs>`_.

#. Fork LFS `GitHub <https://github.com/diefenbach/django-lfs>`_ and send us
   pull requests.

#. Please make sure that you just add related code to your fork. This makes it
   easier to review and pull your code.

#. The code must be put under a `permissive free software licenses
   <http://en.wikipedia.org/wiki/BSD_licenses>`_ like BSD, otherwise we can't
   add it. For instance, code under the GPL or a other `copyleft software
   licenses <http://en.wikipedia.org/wiki/copyleft>`_ won't be added to the
   core.

#. Python code must follow `PEP 8 <http://www.python.org/dev/peps/pep-0008/>`_.
   The maximum of 79 characters per line is the only exception. You may want to
   check your code with `pep8 <http://pypi.python.org/pypi/pep8/>`_. The
   following statement should run without complaints::

     $ pep8 --repeat --ignore=E501 /path/to/lfs

#. Every new feature must have unit tests and documentation.

#. :doc:`All tests must pass <testing>`. Please check this with::

    $ bin/django test lfs.core

#. New features shouldn't make LFS slower. Please see :doc:`benchmarking`.

#. Add yourself to `CREDITS.txt <https://github.com/diefenbach/django-lfs/blob/master/CREDITS.txt>`_.

Contributing Translations
=========================

Please refer to :doc:`/misc/contributing_translations`.
