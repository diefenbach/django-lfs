.. index:: Developing LFS

==============
Developing LFS
==============

This section describes how to work on LFS itself. To build a shop with LFS, see :doc:`/introduction/installation`.

You need git, Python 3.12 or newer, and `uv <https://docs.astral.sh/uv/>`_.

Get the code and run the tests
==============================

#. Fork `django-lfs on GitHub <https://github.com/diefenbach/django-lfs>`_ and clone your fork::

    $ git clone https://github.com/<you>/django-lfs.git
    $ cd django-lfs

#. Install LFS with the tools for its tests (pytest, pytest-django, the default theme)::

    $ uv sync

#. Run the tests::

    $ uv run pytest -n auto

   :doc:`testing` describes the tests in more detail.

Run a shop with your checkout
=============================

To see your changes in a running shop, create a shop from lfs-starter next to the checkout and let it use the
checkout instead of the released package:

#. Clone lfs-starter next to ``django-lfs``::

    $ cd ..
    $ git clone https://github.com/diefenbach/lfs-starter.git shop
    $ cd shop
    $ cp .env.example .env

#. Add these lines to the shop's ``pyproject.toml``::

    [tool.uv.sources]
    django-lfs = { path = "../django-lfs", editable = true }

#. Set up the shop and start it::

    $ uv sync
    $ uv run python manage.py migrate
    $ uv run python manage.py lfs_init
    $ uv run python manage.py createsuperuser
    $ uv run python manage.py runserver

Every change in ``django-lfs`` shows in the shop after a reload; the development server restarts itself when a
Python file changes. The same works for the theme and the add-ons: clone them next to ``django-lfs`` and add them to
``[tool.uv.sources]`` in the same way.

Contributing code
=================

If you consider to contribute code to LFS, please read the following statements first:

#. First of all, you are very welcome!

#. Please discuss new features in an `issue <https://github.com/diefenbach/django-lfs/issues>`_ first. We are
   reluctant to add new things; every new feature should have a real use case.

#. Send your change as a pull request from a branch of your fork. Keep it to one concern; this makes it easier to
   review.

#. The code must be put under a `permissive free software license
   <https://en.wikipedia.org/wiki/BSD_licenses>`_ like BSD, otherwise we can't add it. Code under the GPL or another
   `copyleft license <https://en.wikipedia.org/wiki/Copyleft>`_ won't be added to the core.

#. Python code follows `PEP 8 <https://peps.python.org/pep-0008/>`_, with lines of up to 120 characters. Check it
   with ``uvx ruff check --line-length 120 <your files>``.

#. Every new feature and every bug fix comes with tests and, where users notice it, documentation.

#. Run the tests (``uv run pytest -n auto``) and make sure your change adds no failures.

#. New features shouldn't make LFS slower.

#. Add yourself to `CREDITS.txt <https://github.com/diefenbach/django-lfs/blob/main/CREDITS.txt>`_.

Contributing Translations
=========================

Please refer to :doc:`/misc/contributing_translations`.
