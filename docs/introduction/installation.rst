.. index:: Installation

============
Installation
============

Prerequisites
=============

Make sure you have installed:

* Python 2.6.x or 2.7.x
* A RDBMS of your choice (PostgreSQL, MySQL, SQLite or Oracle)
* libjpeg8-dev zlib1g-dev (for Image handling via Pillow)

.. note::

    Be prepared that we might abandon all other databases but PostgreSQL in one
    of the next releases.

Installation
============

The installation is straightforward and should last just a few minutes. Please
execute following steps:

#. Preferably create a virtualenv and activate it, e.g.::

   $ virtualenv lfs_env

#. Install django-lfs::

   $ pip install django-lfs

#. If you not have an existing one, create a new project::

   $ django-admin startproject <your-projectname>

#. Add the following urls to your project's ``urls.py`` file::

    import django.views.static
    from django.conf import settings
    from django.conf.urls import include

    url(r'', include('lfs.core.urls')),
    url(r'^manage/', include('lfs.manage.urls')),
    url(r'^reviews/', include('reviews.urls')),
    url(r'^media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),

#. Add the following settings to your project's ``settings.py`` file::

    # Django
    from django.utils.translation import ugettext_lazy as _

    INSTALLED_APPS = [
        'lfs_theme',
        ...
        'django.contrib.redirects',
        'django.contrib.sites',
        'compressor',
        'lfs.addresses',
        'lfs.caching',
        'lfs.cart',
        'lfs.catalog',
        'lfs.checkout',
        'lfs.core',
        'lfs.criteria',
        'lfs.customer',
        'lfs.customer_tax',
        'lfs.discounts',
        'lfs.export',
        'lfs.gross_price',
        'lfs.mail',
        'lfs.manage',
        'lfs.marketing',
        'lfs.manufacturer',
        'lfs.net_price',
        'lfs.order',
        'lfs.page',
        'lfs.payment',
        'lfs.portlet',
        'lfs.search',
        'lfs.shipping',
        'lfs.supplier',
        'lfs.tax',
        'lfs.tests',
        'lfs.utils',
        'lfs.voucher',
        'lfs_contact',
        'lfs_order_numbers',
        'lfs_paypal',
        'localflavor',
        'paypal.standard.ipn',
        'portlets',
        'postal',
        'reviews',
    ]

    AUTHENTICATION_BACKENDS = (
        'lfs.customer.auth.EmailBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR + '/media'

    SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"

    SITE_ID = 1

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'compressor.finders.CompressorFinder',
    )

    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR + "/sitestatic"

    # Please note that ``lfs.core.context_processors.main`` has been added
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'lfs.core.context_processors.main',
                ],
            },
        },
    ]

    # LFS
    # see http://docs.getlfs.com/en/latest/developer/settings.html for more
    LFS_AFTER_ADD_TO_CART = "lfs_added_to_cart"
    LFS_RECENT_PRODUCTS_LIMIT = 5

    LFS_CRITERIA = [
        ["lfs.criteria.models.CartPriceCriterion", _(u"Cart Price")],
        ["lfs.criteria.models.CombinedLengthAndGirthCriterion", _(u"Combined Length and Girth")],
        ["lfs.criteria.models.CountryCriterion", _(u"Country")],
        ["lfs.criteria.models.HeightCriterion", _(u"Height")],
        ["lfs.criteria.models.LengthCriterion", _(u"Length")],
        ["lfs.criteria.models.WidthCriterion", _(u"Width")],
        ["lfs.criteria.models.WeightCriterion", _(u"Weight")],
        ["lfs.criteria.models.ShippingMethodCriterion", _(u"Shipping Method")],
        ["lfs.criteria.models.PaymentMethodCriterion", _(u"Payment Method")],
    ]

    LFS_ORDER_NUMBER_GENERATOR = "lfs_order_numbers.models.OrderNumberGenerator"
    LFS_DOCS = "http://docs.getlfs.com/en/latest/"

    LFS_INVOICE_COMPANY_NAME_REQUIRED = False
    LFS_INVOICE_EMAIL_REQUIRED = True
    LFS_INVOICE_PHONE_REQUIRED = True

    LFS_SHIPPING_COMPANY_NAME_REQUIRED = False
    LFS_SHIPPING_EMAIL_REQUIRED = False
    LFS_SHIPPING_PHONE_REQUIRED = False

    LFS_PAYMENT_METHOD_PROCESSORS = [
        ["lfs_paypal.processor.PayPalProcessor", _(u"PayPal")],
    ]

    LFS_PRICE_CALCULATORS = [
        ['lfs.gross_price.calculator.GrossPriceCalculator', _(u'Price includes tax')],
        ['lfs.net_price.calculator.NetPriceCalculator', _(u'Price excludes tax')],
    ]

    LFS_SHIPPING_METHOD_PRICE_CALCULATORS = [
        ["lfs.shipping.calculator.GrossShippingMethodPriceCalculator", _(u'Price includes tax')],
        ["lfs.shipping.calculator.NetShippingMethodPriceCalculator", _(u'Price excludes tax')],
    ]

    LFS_UNITS = [
        _(u"l"),
        _(u"m"),
        _(u"cm"),
        _(u"lfm"),
        _(u"Package(s)"),
        _(u"Piece(s)"),
    ]
    LFS_PRICE_UNITS = LFS_BASE_PRICE_UNITS = LFS_PACKING_UNITS = LFS_UNITS

    # Paypal
    LFS_PAYPAL_REDIRECT = True
    PAYPAL_RECEIVER_EMAIL = "info@yourbusiness.com"
    PAYPAL_IDENTITY_TOKEN = "set_this_to_your_paypal_pdt_identity_token"

    # Reviews
    # see http://django-reviews.readthedocs.io/en/latest/#settings for more
    REVIEWS_SHOW_PREVIEW = False
    REVIEWS_IS_NAME_REQUIRED = False
    REVIEWS_IS_EMAIL_REQUIRED = False
    REVIEWS_IS_MODERATED = False

Optionally you might add::

    # Django
    # see https://docs.djangoproject.com/en/1.10/topics/cache/ for more.
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
    }

    # Compressor
    # see http://django-compressor.readthedocs.io/en/latest/settings/ for more
    COMPRESS_CSS_FILTERS = [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.CSSCompressorFilter',
    ]
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True

#. $ python manage.py migrate

#. $ python manage.py lfs_init

#. $ python manage.py runserver

#. Browse to http://localhost:8000

.. note::

    If you encounter problems, please see :ref:`trouble shooting
    <trouble_shooting_installation>`.

.. note::

    If you're setting up a production environment then you should not use Django's builtin development
    server (bin/django runserver). Instead, you'll probably want to use uWsgi or Gunicorn servers.
    Check Django (and uWsgi/Gunicorn) documentation for details.

.. note::

    For production environments you're supposed to change robots.txt file (otherwise bots/crawlers like google bot will
    not be allowed to scan your site, which is not what you probably want). Default version of robots.txt is located
    at lfs_theme application: templates/lfs/shop/robots.txt.
    You should create your own 'mytheme' app with structure like:
    templates/lfs/shop/robots.txt and place it in settings.INSTALLED_APPS before(!) 'lfs_theme'. Also note, that in
    production environment it is good to serve robots.txt directly from HTTP server like nginx or Apache.

Migration from version 0.9 to version 0.10 and higher
=====================================================

Migration starting from 0.10 is based on Django’s default migrations, see:
https://docs.djangoproject.com/en/1.8/topics/migrations/

#. Install the new LFS version

#. Backup your existing database

#. Enter your existing database to lfs_project/settings.py

#. $ bin/django migrate

Migration from versions 0.5 - 0.8 to version 0.10
=================================================

Migrations from 0.5 - 0.8 to version 0.10 needs an intermediate step through
version 0.9.

Migration from versions 0.5 - 0.8 to version 0.9
================================================

Migration from versions 0.5 - 0.8 to version 0.9 can be done with a migration command (``lfs_migrate``)
which migrates existing databases up to version 0.9.

#. Install the 0.9

#. Backup your existing database

#. Enter your existing database to lfs_project/settings.py

#. $ bin/django syncdb

#. $ bin/django lfs_migrate

What's next?
============

Move on to :doc:`getting_started`.
