==========
django-lfs
==========

**LFS (Lightning Fast Shop) is an open source online shop built on Python and Django.**

It covers the whole way from the catalog to the paid order and comes with its own
management interface for the daily work in a shop. Prices, taxes, shipping and
payment follow configurable rules instead of code changes in the core.

* Open source since 2009, more than 3,000 commits, BSD licensed
* In production in several B2B and B2C shops
* Actively developed: runs on Django 5.2 LTS and Python 3.12+, with more than
  500 commits since 2025

Features
========

**Catalog**
  Categories, products with variants and properties, accessories, attachments,
  manufacturers and suppliers. Filterable product lists and a search.

**Prices and taxes**
  Net and gross price calculation, and tax rates that depend on the product
  and on the customer's country.

**Shipping and payment**
  Any number of shipping and payment methods with their own prices and
  delivery times. Criteria decide which methods a customer is offered, for
  example by cart value, country, weight or package dimensions.

**Checkout and orders**
  A one-page checkout, order management with states, and order mails.

**Marketing**
  Vouchers, discounts, top sellers, featured products and product reviews.

**Content**
  Pages, static blocks and portlets to build the shop's pages without
  touching templates.

**SEO**
  Structured data (JSON-LD), also for product variants, canonical URLs and a
  sitemap with products, categories and manufacturers.

**Management interface**
  A dedicated interface for products, orders, customers and content, built
  with Bootstrap 5 and HTMX. Exports, for example for price comparison sites.

**Languages**
  Translations for Czech, Dutch, English, French, German, Italian, Polish and
  Spanish.

Architecture
============

LFS is a regular Django project made of separate apps (``lfs.catalog``,
``lfs.cart``, ``lfs.checkout``, ``lfs.order``, ``lfs.manage`` and others). If
you know Django, you will find your way around quickly.

Shops differ, so the parts that differ are pluggable. You write a class,
register it in the settings, and keep your own requirements out of the core:

* **Price calculators** (``lfs.plugins.PriceCalculator``) define how a product
  price is calculated.
* **Payment processors** (``lfs.plugins.PaymentMethodProcessor``) connect
  payment providers.
* **Shipping price calculators**
  (``lfs.plugins.ShippingMethodPriceCalculator``) calculate shipping costs.
* **Criteria** (``lfs.criteria.models.Criterion``) decide when a shipping
  method, payment method, discount or tax rate applies.

Requirements
============

* Python 3.12 or newer
* Django 5.2 (LTS)
* A database supported by Django; PostgreSQL is used in production

Installation
============

To try LFS, start the demo shop with `Docker <https://www.docker.com/>`_::

    docker run --rm -p 8000:8000 ghcr.io/diefenbach/lfs

Then open http://localhost:8000/ for the shop and
http://localhost:8000/manage/dashboard/ for the management interface (user
``admin``, password ``admin``). The image is for trying LFS only; see
`lfs-docker <https://github.com/diefenbach/lfs-docker>`_.

For a real shop start from
`lfs-starter <https://github.com/diefenbach/lfs-starter>`_: a ready Django
project with LFS, the default theme and the standard add-ons, configured
through environment variables. To add LFS to an existing Django project
instead, follow
`docs/introduction/installation.rst <docs/introduction/installation.rst>`_.

Documentation
=============

The documentation is part of this repository, in the `docs <docs>`_ folder,
and is built with Sphinx (see `docs/README.md <docs/README.md>`_). It
explains the concepts, the management interface and how to extend LFS.

Parts of it still describe older releases and are being revised. If something
does not match the code, the code is right; please open an issue.

Tests
=====

LFS has more than 2,500 tests, written with pytest, pytest-django and
factory_boy. The management interface is also tested in a real browser with
Playwright (see `lfs/manage/tests_e2e <lfs/manage/tests_e2e>`_).

Related packages
================

Themes and add-ons live in their own repositories:

* `lfs-starter <https://github.com/diefenbach/lfs-starter>`_: a new shop, ready to run
* `lfs-theme <https://github.com/diefenbach/lfs-theme>`_: the default shop theme
* `lfs-paypal <https://github.com/diefenbach/lfs-paypal>`_ and
  `lfs-stripe <https://github.com/diefenbach/lfs-stripe>`_: payment providers
* `lfs-bulk-prices <https://github.com/diefenbach/lfs-bulk-prices>`_: graduated prices
* `lfs-samples <https://github.com/diefenbach/lfs-samples>`_: free samples of products
* `lfs-canonical <https://github.com/diefenbach/lfs_canonical>`_: canonical URLs
* `lfs-cookie-consent <https://github.com/diefenbach/lfs_cookie_consent>`_ and
  `lfs-gtm <https://github.com/diefenbach/lfs-gtm>`_: consent and tracking
* `lfs-carousel <https://github.com/diefenbach/lfs-carousel>`_: image carousel

LFS itself depends on `lfs-order-numbers <https://github.com/diefenbach/lfs-order-numbers>`_,
`lfs-contact <https://github.com/diefenbach/lfs-contact>`_,
`lfs-postal <https://github.com/diefenbach/django-postal>`_,
`django-portlets <https://github.com/diefenbach/django-portlets>`_ and
`django-reviews <https://github.com/diefenbach/django-reviews>`_.

Contributing and support
========================

Bug reports and pull requests are welcome in the
`issue tracker <https://github.com/diefenbach/django-lfs/issues>`_.

LFS is developed by `IQ++ <https://www.iqpp.de>`_. If you plan a shop or need
an extension, get in touch there.

License
=======

BSD 3-Clause, see `LICENSE.txt <LICENSE.txt>`_. The people who built LFS are
listed in `CREDITS.txt <CREDITS.txt>`_, the changes of each release in
`HISTORY.txt <HISTORY.txt>`_.

The management interface bundles third-party libraries in
``lfs/manage/static/lfs/manage/vendor/``:

* TinyMCE: GPL-2.0-or-later (``tinymce/license.md``); LFS configures it with
  ``license_key: 'gpl'``. A shop that distributes LFS with TinyMCE must follow
  the GPL, or use a commercial TinyMCE license. The source code of the bundled
  version (8.9.3) is at https://github.com/tinymce/tinymce/tree/8.9.3.
* Bootstrap, Bootstrap Icons, flatpickr, SortableJS: MIT
* htmx: 0BSD
