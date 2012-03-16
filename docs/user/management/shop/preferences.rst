.. index:: Google Analytics, Price Calculator

.. _preferences:

===========
Preferences
===========

This section describes the preferences management interface.


.. _preferences_shop:

Shop
====

General
-------

Name
    The name of the shop. It will be used as prefix of all pages of the shop and
    is therefore very important for the appearance within SERPs.

Shop owner
    The shop owner. This can be used on several places within the shop, e.g.
    within the thank-you page.

E-Mails
-------

From e-mail address
    This e-mail address will be used as sender for all outgoing mails.

Notification email addresses
    This e-mail addresses will be used as receiver for all incoming mails.

Google
------

Google Analytics ID
    The unique Google Analytics ID of the shop.

Google Analytics Site Tracking
    If checked the shop is tracked with Google Analytics.

Google Analytics E-Commerce Tracking
    If checked the shop is tracked with Google Analytics E-Commerce feature.

Checkout
--------

Checkout type
    There are three checkout types:

    Anonymous and Authenticated
        The customer can decide whether he registers and login to the shop
        or checkout without registration.

    Anonymous only
        Registration is not available

    Anonymous only
        All customers have to register and login to the shop.

Confirm TOC
    If checked the customers have to confirm the terms of contract of the shop
    in order to checkout.

Content
-------

Description
    The description of the shop. This is displayed within the front page of the
    shop.

Static block
    The static block is displayed on top of the front page of the shop. See
    :doc:`/user/management/html/static_block` for more.

Image
    The image of the shop.


.. _preferences_default_values:

Default Values
==============

Price calculator
----------------

Price calculator
    The default price calculator of the shop. If a product doesn't have an
    explicit price calculator this one is used.

Format
------

Product cols
    Default value for amount of displayed columns within a category if the
    category displays products.

Product rows
    Default value for amount of displayed rows within a category if the
    category displays products.

Category cols
    Default value for amount of displayed columns within a category if the
    category displays sub categories.

Countries
---------

Invoice countries
    Available countries within the invoice address.

Shipping countries
    Available countries within the shipping address.

Default shipping country
    The default shipping country within addresses. This country will be used to
    calculate shipping price if the shop customer doesn't have select a country
    yet.

Localization
------------

Default shop locale
    This locale of the shop. This is used for localization of numbers and
    currencies, etc. You can find more information here: http://en.wikipedia.org/wiki/Locale

Use international currency codes
    If checked the international currency code of the currency is used, e.g. USD
    or EUR.


.. _preferences_order_numbers:

.. index:: Order Numbers

Order Numbers
=============

Last order number
    This field stores the integer part of the last given order number, which is
    the base for the next given order number.

Format
    This field stores the format of the order number. The integer part which is
    stored in ``Last order number`` can be formatted with `Python's string
    formatting operators <http://docs.python.org/library/stdtypes.html#string-formatting-operations>`_,
    e.g.::

        DOE-%04d-2012 will return DOE-0001-2012

    Whereas ``%04d`` represents the integer part of the order number, which is
    stored in ``Last order number``.

.. index:: SEO

.. _preferences_seo:

SEO
===

This tab is used to optimize the start page for search engines. One can enter
data for all usual HTML meta data fields.

Meta title
    This is displayed within the ``meta title`` tag of the start page. By
    default the ``Name`` field of the ``Shop`` tab is used (see above).

Meta keywords
    This is displayed within the ``meta keywords`` tag of the start page.

Meta description
    This is displayed within the ``meta description`` tag of the start page.

.. note::

    Following placeholder can be used within these fields:

    <name>
        The name of the product.

.. _preferences_portlets:

.. index:: Portlets

Portlets
========

This tab is used to assign :term:`Portlets` to the shop.

Slots
    Here you can see all directly assigned portlets to the shop. In order
    to edit a portlet click on row of the portlet. In order to delete a
    portlet click on the red cross beside the portlet. You can also change
    the position of the portlets by clicking on the up and down arrows beside
    the portlets.

Add new Portlet
    In order to add a portlet to the shop select the type of portlet and
    click on ``Add portlet``.
