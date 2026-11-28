.. index:: Installation

============
Installation
============

Requirements
============

* Python 3.12 or newer
* Django 5.2 (installed with django-lfs)
* A database supported by Django. PostgreSQL is recommended for a shop in production; SQLite is fine to try LFS.

There are two ways to install LFS: start a new shop from the template lfs-starter (recommended), or add LFS to an
existing Django project.

New shop with lfs-starter
=========================

`lfs-starter <https://github.com/diefenbach/lfs-starter>`_ is a ready Django project with LFS, the default theme
and the standard add-ons. Its settings come from environment variables, so the same code runs locally and in
production. It uses `uv <https://docs.astral.sh/uv/>`_::

    $ git clone https://github.com/diefenbach/lfs-starter.git myshop && cd myshop
    $ cp .env.example .env
    $ uv sync
    $ uv run python manage.py migrate
    $ uv run python manage.py lfs_init
    $ uv run python manage.py createsuperuser
    $ uv run python manage.py runserver

Then open http://127.0.0.1:8000/ for the shop and http://127.0.0.1:8000/manage/dashboard/ for the management
interface (log in with the superuser). Without ``POSTGRES_DB`` in ``.env`` the shop uses SQLite.

Optional add-ons such as PayPal or Stripe are extras of the project, for example ``uv sync --extra stripe``. The
`README of lfs-starter <https://github.com/diefenbach/lfs-starter#readme>`_ lists them and the settings for
production.

Add LFS to an existing Django project
=====================================

#. Install LFS and a theme::

    $ pip install django-lfs lfs-theme

#. Put the theme and the apps LFS needs into ``INSTALLED_APPS``. ``LFS_APPS`` contains the Django apps, LFS, and
   the packages LFS depends on, in an order that works. The theme goes first, so its templates win::

    from lfs.settings import LFS_APPS

    INSTALLED_APPS = [
        "lfs_theme",
        *LFS_APPS,
        # LFS add-ons and your own apps
    ]

#. Add the settings LFS relies on::

    AUTHENTICATION_BACKENDS = [
        "lfs.customer.auth.EmailBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]
    LOGIN_URL = "/login/"
    LOGIN_REDIRECT_URL = "/manage/dashboard/"

    SITE_ID = 1
    SESSION_SERIALIZER = "lfs.core.pickle_serializer.PickleSerializer"

    # LFS's migrations use AutoField ids; with BigAutoField (the default of startproject) Django would want to
    # change every LFS table.
    DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        "compressor.finders.CompressorFinder",
    ]
    STATIC_ROOT = BASE_DIR / "static"
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"

    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
    CRISPY_TEMPLATE_PACK = "bootstrap5"

   and the context processor ``lfs.core.context_processors.main`` to ``TEMPLATES``::

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "lfs.core.context_processors.main",
                ],
            },
        },
    ]

   LFS has defaults for its own settings (price calculators, units, criteria, ...), so you set only those you want
   to change, for example ``LFS_CURRENCY = "EUR"``; see :doc:`/developer/settings`.

#. Add the URLs to the project's ``urls.py``::

    from django.conf import settings
    from django.conf.urls.static import static
    from django.contrib import admin
    from django.urls import include, path

    urlpatterns = [
        path("", include("lfs.core.urls")),
        path("manage/", include("lfs.manage.urls")),
        path("admin/", admin.site.urls),
        path("reviews/", include("reviews.urls")),
        path("captcha/", include("captcha.urls")),
        path("theme/", include("lfs_theme.urls")),
    ]

    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#. Create the tables, the shop, and a user for the management interface, then start the development server::

    $ python manage.py migrate
    $ python manage.py lfs_init
    $ python manage.py createsuperuser
    $ python manage.py runserver

#. Open http://127.0.0.1:8000/ for the shop and http://127.0.0.1:8000/manage/dashboard/ for the management
   interface.

.. _installation_addons:

Add-ons
=======

Each add-on is a package of its own. Install it, add its app to ``INSTALLED_APPS`` after ``*LFS_APPS``, include its
URLs if it has any, and run ``python manage.py migrate``. The add-on's README names its settings and URLs; the
``urls.py`` of lfs-starter shows them all.

=================== ======================== =========================================================
Package             App                      Purpose
=================== ======================== =========================================================
lfs-paypal          ``lfs_paypal``           Payment with PayPal
lfs-stripe          ``lfs_stripe``           Card payment with Stripe
lfs-bulk-prices     ``lfs_bulk_prices``      Price tiers by quantity
lfs-canonical       ``lfs_canonical``        Canonical URLs
lfs-cookie-consent  ``lfs_cookie_consent``   Cookie consent banner
lfs-gtm             ``lfs_gtm``              Google Tag Manager with Consent Mode (needs lfs-cookie-consent)
lfs-carousel        ``lfs_carousel``         Image carousel
lfs-samples         ``lfs_samples``          Product samples
=================== ======================== =========================================================

Production
==========

* Set ``DEBUG = False``, a secret ``SECRET_KEY``, ``ALLOWED_HOSTS`` and ``CSRF_TRUSTED_ORIGINS``, and an e-mail
  server: the shop sends the order mails.
* Use PostgreSQL and add ``django.contrib.postgres`` to ``INSTALLED_APPS``; the search then ignores accents.
* Run ``python manage.py collectstatic`` on every deployment.
* Run the project with an application server such as gunicorn behind a web server (nginx, Caddy) that terminates
  HTTPS and serves the static and uploaded files. Do not use ``runserver`` in production.
* The theme's ``robots.txt`` is the template ``lfs/shop/robots.txt``. To change it, put a template with the same path
  into your project's templates or your own theme.

What's next?
============

Move on to :doc:`getting_started`. If you upgrade an existing shop, read :doc:`upgrade_notes` first. If something
does not work, see :doc:`/misc/trouble_shooting`.
