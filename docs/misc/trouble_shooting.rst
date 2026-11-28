================
Trouble Shooting
================

Problems that come up when setting up a shop with LFS 1.0, and what helps.

.. _trouble_shooting_installation:

Installation
============

``ImproperlyConfigured: COMPRESS_ROOT defaults to STATIC_ROOT``
    django-compressor needs ``STATIC_ROOT``. Set it, e.g. ``STATIC_ROOT = BASE_DIR / "static"``.

The login page fails with an error 500 (``CRISPY_TEMPLATE_PACK``)
    Set ``CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"`` and ``CRISPY_TEMPLATE_PACK = "bootstrap5"``.

``makemigrations`` wants to change the ``id`` of every LFS model
    The project uses ``BigAutoField`` (the default of ``startproject``); LFS's migrations use ``AutoField``. Set
    ``DEFAULT_AUTO_FIELD = "django.db.models.AutoField"``. Never write migrations into the installed LFS packages.

``/manage/`` shows "Page not found"
    The management interface starts at ``/manage/dashboard/``.

See :doc:`/introduction/installation` for all settings LFS needs.

The Shop
========

The checkout offers no country, or only USA
    The shop offers only countries that exist in the database, and ``lfs_init`` creates only USA. Add your countries
    in Django's admin under ``Core / Countries`` and select them in ``Shop / Preferences``, tab ``Default Values``.

``Prepayment`` is offered twice
    ``lfs_init`` of LFS 1.0.0 created it twice when lfs-paypal was not installed. Delete one of them under ``Shop /
    Payment Methods``; LFS 1.1.0 creates it once.

The shop has no sidebars
    The default theme shows a sidebar only when its slot has portlets, and ``lfs_init`` assigns none. Add portlets
    under ``Shop / Preferences``, tab ``Portlets``, e.g. the filter (:doc:`/user/howtos/how_to_filters`).

The management interface shows no help link
    Set ``LFS_DOCS = "https://docs.django-lfs.com/"``; without it the help menu is hidden.

The shop shows old content
    LFS caches categories, products and more. Clear the cache under ``Utils / Miscellaneous``.
