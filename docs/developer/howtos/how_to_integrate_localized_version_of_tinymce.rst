=============================================
How to integrate localized version of TinyMCE
=============================================

The management interface edits texts (descriptions, pages, static blocks) with TinyMCE 8, which LFS ships in
``lfs/manage/static/lfs/manage/vendor/tinymce/`` without language files. Its menus and dialogs are therefore in
English, whatever the language of the management interface.

To show them in another language, e.g. German:

#. Download the language file ``de.js`` for TinyMCE 8 from https://www.tiny.cloud/get-tiny/language-packages/.

#. Put it into the static files of an app of your project, at the path TinyMCE expects:
   ``<your app>/static/lfs/manage/vendor/tinymce/langs/de.js``.

#. Copy ``lfs/manage/static/lfs/manage/js/shared.js`` to ``<your app>/static/lfs/manage/js/shared.js`` and add
   ``language: 'de',`` to the options of ``tinymce.init``.

#. List your app **before** the LFS apps in ``INSTALLED_APPS``, so that its static files win, and run ``python
   manage.py collectstatic`` in production.

.. note::

    The copied ``shared.js`` does not get the changes of later LFS releases; compare it when you upgrade.
