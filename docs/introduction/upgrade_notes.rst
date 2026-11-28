.. index:: Upgrade notes

=============
Upgrade notes
=============

Below is a description of changes that are useful to know about when upgrading LFS to a newer version. The full
list of changes is in ``HISTORY.txt``.

Upgrading from 0.x to 1.0
=========================

LFS 1.0 needs Python 3.12 or newer and Django 5.2. It is an installable package with declared dependencies; the
theme and several add-ons are packages of their own.

#. Back up the database and try the upgrade on a copy first.

#. Install the new packages: ``django-lfs``, a theme (``lfs-theme`` or your own), and the add-ons the shop uses,
   for example ``lfs-paypal`` or ``lfs-bulk-prices`` (see :ref:`the list of add-ons <installation_addons>`).
   portlets, reviews, postal, contact form, and order numbers are now django-portlets 2, django-reviews 2,
   lfs-postal 1, lfs-contact 2, and lfs-order-numbers 2; django-lfs installs them.

#. Replace the list of LFS apps in ``INSTALLED_APPS`` with ``*LFS_APPS`` from ``lfs.settings``, keep the theme
   before it and the add-ons after it. Compare the result with your old list: apps you added yourself stay.

#. Remove the LFS settings that match the defaults (price calculators, units, criteria, order number generator);
   ``lfs.settings.DEFAULTS`` lists them. Keep only those you changed.

#. Update the Django settings that changed with Django 5.2 and LFS 1.0:

   * ``SESSION_SERIALIZER = "lfs.core.pickle_serializer.PickleSerializer"`` (Django no longer ships a pickle
     serializer).
   * ``CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"`` and ``CRISPY_TEMPLATE_PACK = "bootstrap5"``.
   * URLs with ``path()`` instead of ``url()``; the theme needs ``path("theme/", include("lfs_theme.urls"))`` and
     the captcha ``path("captcha/", include("captcha.urls"))``.

   :doc:`installation` shows the complete settings and URLs.

#. Set the settings that your add-ons need in their new versions; each add-on's README lists them.

#. Run ``python manage.py migrate``. Migrations no longer depend on the shop's settings.

#. Review the templates that override LFS templates, above all those of the management interface: it has been
   rewritten with Bootstrap 5 and htmx.

#. Check the shop on the copy before you switch: prices, shipping costs, the checkout with every payment method,
   the order mails, and the management interface.


Upgrading from 0.7.x to 0.8.x
=============================

This is not full reference of changes but at least some of them are described:

* currency templatetag always returns HTML now, eg. <span class="money">Fr. 999</span>, previously HTML was only returned for negative values
* currency templatetag in text email templates (lfs_theme/templates/lfs/mail/order_details.txt) was removed in favour of currency_text templatetag. The latter one doesn't return HTML (ever).
* lfs/base.html has slightly different structure to the footer and colophon sections due to incorrect width of these elements in previous layout.
  div.colophon-inner and div.footer-inner html elements were added, both with padding: 10px set in main.css.
  padding: 10px was removed from '#footer .container' and '#colophon .container' in main.css
* update_editor method in lfs_tinymce.js has been modified and requires tinymce 3.5.8 which is now being used.
  References to tinymce were changed in base.html and lfs_tinymce.js
* filter portlet has been updated to allow for manufacturer filtering and because of that its template:
  lfs_theme/templates/lfs/portlets/filter.html was modified - manufacturer filtering section has been added
* Small change at lfs/templates/manage/product/product.html - removed onkeypress from filter input element in favour
  of css class 'disable-enter-key'. Changed lfs.manage.js to add event handler for 'disable-enter-key'.
* Added new ORDER state: PREPARED that can be used to mark orders as prepared to be sent.
* Added new signal and setting that allows defining extra ORDER_STATES. Signal is order_state_changed and option is
  LFS_EXTRA_ORDER_STATES. New states should start with id 20 or higher to avoid conflicts with built in states.
* Use 'SHOP' instead of 'shop' in lfs/shop/shop.html
* Added position column to PropertyGroups and ability to order these with drag & drop in management panel - modified lfs.manage.js
  and management template for property groups.
* Added LFS_CHECKOUT_NOT_REQUIRED_ADDRESS setting. This allows to change address that is not required at checkout page.
  Changed one_page_checkout.html template, lfs.js and OnePageCheckout Form.
* refactored lfs.manage.js - do not use ``live`` anymore. Updated manage/export/export.html, manage/export/export_inline.html,
  manage/manufactuers/manufacturer.html and manage/manufacturers/manufacturer_inline.html to use data-url instead of just 'data'
  and use elem.data('something') in JavaScript
* added <div id="portlets-dialog" title="{% trans "Portlets dialog" %}"></div> to base.html to handle properly inerting images to TinyMCE within portlets dialog
  (changes to lfs.manage.js with portlets dialog)
* added some SEO related attributes to templates and canonical tags for variants
* modified catalog/views.py -> category_products and catalog/views.py -> category_categories return value, so that it now contains
  pagination data for use in main template (SEO optimization with rel="next/prev" (template: lfs/catalog/category_base.html)
* modified mimetype returned by ajax calls to: application/json. This requireS changes in javascript ajax calls:
  lfs.js, lfs.manage.js, lfs_tinymce.js, manage/product/attachments.html(!)
* moved javascript code from manage/product/images.html to lfs.manage.product.js and updated to use proper mimetypes in responses

Older versions
==============

* From 0.9 to 0.10 and higher: LFS uses Django's migrations; back up the database, install the new version, and
  run ``migrate``.
* From 0.5 – 0.8: upgrade to 0.9 first with its command ``lfs_migrate``, then continue as above.
