=========================
Contributing translations
=========================

LFS is translated with Django's translation system. Contributions are welcome as pull requests on GitHub.

Where the translations are
==========================

* django-lfs: one catalog for all its apps, ``lfs/core/locale/<language>/LC_MESSAGES/django.po``. It covers the
  management interface and the texts of LFS's Python code.
* lfs-theme: the texts of the shop, ``lfs_theme/locale/<language>/LC_MESSAGES/django.po`` in its repository.

You need GNU gettext (``xgettext``, ``msgfmt``), e.g. ``brew install gettext`` or ``apt install gettext``, and a
checkout set up as described in :doc:`/developer/developing`.

Update and translate the catalog of django-lfs
==============================================

#. Collect the texts. The catalog lists its sources relative to ``lfs/``, so run ``makemessages`` there, through a
   temporary link to the catalog::

    $ cd lfs
    $ ln -s core/locale locale
    $ uv run django-admin makemessages -l de --ignore "*/tests/*" --ignore "tests_e2e/*" --ignore "node_modules/*"
    $ rm locale

   Replace ``de`` with your language. New texts get an empty ``msgstr``; changed ones are marked ``fuzzy``.

#. Translate ``lfs/core/locale/de/LC_MESSAGES/django.po`` with an editor such as Poedit, or any text editor: fill
   the empty ``msgstr`` entries and check the ``fuzzy`` ones (then remove the ``fuzzy`` flag).

#. Compile it and look at the result in a shop with your checkout (see :doc:`/developer/developing`)::

    $ cd lfs/core
    $ uv run django-admin compilemessages -l de

#. Commit the ``.po`` and ``.mo`` files and open a pull request.

For lfs-theme run ``makemessages`` and ``compilemessages`` in its ``lfs_theme`` directory; there the catalog is in
the usual place, so no link is needed.

See also
========

* `Translation in Django <https://docs.djangoproject.com/en/5.2/topics/i18n/translation/>`_
