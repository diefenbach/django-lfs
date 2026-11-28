.. index:: Google Analytics, Price Calculator

.. _preferences:

===========
Preferences
===========

This section describes the preferences of the shop (``Shop / Preferences``).

.. image:: /images/manage_shop_data.png
   :alt: The Data tab of the shop preferences

.. _preferences_shop:

Data
====

Click ``Save Shop Data`` to save the changes of this tab.

General
-------

Name
    The name of the shop. It is part of the title of every page and therefore important for search engines.

Shop owner
    The owner of the shop, used in several places, e.g. on the thank-you page.

E-Mails
-------

From e-mail address
    The sender of all e-mails the shop sends.

Notification email addresses
    The addresses that get the notifications of the shop, e.g. about new orders. Separate several addresses by
    commas or line breaks.

Checkout
--------

Checkout type
    Anonymous and Authenticated
        The customer can register and log in, or check out without registering.

    Anonymous only
        Customers check out without registering.

    Authenticated only
        Customers have to register and log in to check out.

Confirm TOC
    If checked, customers have to confirm the terms and conditions of the shop to check out.

Google
------

Google Analytics ID
    The Google Analytics ID of the shop.

Google Analytics Site Tracking
    If checked, the shop is tracked with Google Analytics.

Google Analytics E-Commerce Tracking
    If checked, orders are tracked with the e-commerce feature of Google Analytics.

.. note::

    The default theme lfs-theme does not use these fields: they take effect only in a theme that includes the
    template tags ``google_analytics_tracking`` and ``google_analytics_ecommerce`` (from ``lfs_tags``). For Google
    Tag Manager with a consent banner use the add-ons lfs-gtm and lfs-cookie-consent.

Content
-------

Description
    The description of the shop, displayed on the start page.

Image
    The image of the shop.

Static block
    A :doc:`static block </user/management/html/static_block>` displayed on the start page.

.. _preferences_default_values:

Default Values
==============

.. image:: /images/manage_shop_default_values.png
   :alt: The Default Values tab of the shop preferences

Click ``Save Default Values`` to save the changes of this tab.

Price Calculator
----------------

Price calculator
    The price calculator of all products that do not select one themselves.

Delivery Time
-------------

Delivery time
    The delivery time used when none can be calculated for a product.

Countries
---------

Default shipping country
    Preselected in addresses. It is used to calculate the shipping costs as long as the customer has not selected
    a country.

Invoice countries
    The countries customers can select in the invoice address.

Shipping countries
    The countries customers can select in the shipping address.

.. note::

    The lists offer the countries in the database; add more in Django's admin under ``Core / Countries`` (see
    :doc:`/introduction/getting_started`).

Returns
-------

LFS writes the return policy into the structured data (schema.org ``MerchantReturnPolicy``) of every product, so
search engines can show it, but only once the ``Return policy page`` is set: until then LFS makes no statement
about returns. Check the other fields before you set the page; their defaults are 14 days and free return.

Return days
    The days a customer has to return a product; ``0`` means no returns.

Return fees
    ``Free return`` or ``Customer pays the return``.

Return method
    ``By mail`` or ``In store``.

Return policy page
    Path or URL of the page with the return policy, e.g. ``/page/return-policy/``. Without it the shop publishes no
    return policy.

.. _preferences_order_numbers:

.. index:: Order Numbers

Order Numbers
=============

Last Order Number
    The number of the last order. The next order gets this number plus one.

Format
    The format of the order number. ``%d`` stands for the number, ``%04d`` for the number with at least four
    digits, e.g. ``ACME-%04d`` gives ``ACME-0001``.

Click ``Save Order Numbers`` to save the changes.

.. index:: SEO

.. _preferences_seo:

SEO
===

This tab is used to optimize the start page for search engines. Click ``Save SEO Data`` to save the changes.

Meta title
    Displayed in the title tag of the start page. The default is ``<name>``, the name of the shop.

Meta description
    Displayed in the meta description tag of the start page.

Meta keywords
    Displayed in the meta keywords tag of the start page.

.. _preferences_portlets:

.. index:: Portlets

Portlets
========

This tab is used to assign :term:`portlets` to the shop. Categories, products and pages inherit them unless they
block them.

Slots
    Lists the portlets of the shop, per slot. Click the pencil to edit a portlet and the trash can to delete it.
    Drag a portlet to change its position or to move it to the other slot.

Add new portlet
    Select the ``Portlet Type`` and click ``Add portlet``.
