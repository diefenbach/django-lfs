.. _getting_started:

===============
Getting Started
===============

This document explains the first steps after the shop has been installed (see :doc:`/introduction/installation`).
It leads from an empty shop to a first product that customers can buy.

``lfs_init`` has already created the shop with a delivery time, a shipping method ``Standard``, the payment methods
``Direct debit``, ``Cash on delivery`` and ``Prepayment``, the pages ``Terms and Conditions`` and ``Imprint``, and the country ``USA``.

Log In
======

#. Browse to http://127.0.0.1:8000/manage/dashboard/.

#. Log in with the user you created with ``createsuperuser``.

The menu at the top leads to all parts of the management interface: ``Shop``, ``Catalog``, ``Properties``,
``HTML``, ``Customers``, ``Marketing`` and ``Utils``.

Add Countries
=============

The shop offers only the countries that exist in the database; ``lfs_init`` creates ``USA``. Add the countries you
sell to in Django's admin:

#. Browse to http://127.0.0.1:8000/admin/ and go to ``Core / Countries``.

#. Click ``Add country``, enter the ``Country code`` (ISO 3166, for instance ``DE``) and the ``Name``, and save.

Enter Shop Preferences
======================

#. Go to ``Shop / Preferences``. The ``Data`` tab opens.

#. Enter the ``Name``. This is the name of the shop, for instance ``ACME Inc``, which is used in several places,
   e.g. as part of the meta title of all HTML pages.

#. Enter the ``Shop owner``. This is the full name of the shop owner.

#. Enter the ``From e-mail address``. This address is the sender of all e-mails the shop sends, e.g. the order
   confirmation to the customer.

#. Enter the ``Notification email addresses``. All notifications go to these addresses, for example when an order
   has been submitted.

#. Click ``Save Shop Data``.

#. Go to the ``Default Values`` tab.

#. Select the ``Price calculator``. This is the default for all products that do not select one themselves.

#. Select the ``Invoice countries`` and ``Shipping countries``. Customers can choose from these in the checkout.

#. Select the ``Default shipping country``. It is preselected in the checkout.

#. Click ``Save Default Values``.

Add Product Taxes
=================

#. Go to ``Shop / Product Taxes`` and click ``Create Your First Tax``.

#. Enter the ``Rate`` in percent, for instance 19.0.

#. Click ``Add Tax``.

Check the Delivery Time
=======================

#. Go to ``Shop / Delivery Times``. ``lfs_init`` has created a delivery time of 1 to 2 days.

#. Change ``Min``, ``Max`` and ``Unit`` if your delivery takes longer, and click ``Save``.

Add Categories
==============

#. Go to ``Catalog / Categories`` and click ``Create Your First Category``.

#. Enter a ``Name`` and a ``Slug``. The slug is the part of the URL, for instance ``chairs``.

#. Click ``Add Category``. The ``Data`` tab of the new category opens.

#. Enter a ``Description``. It is displayed on the page of the category.

#. Click ``Save Category Data``.

#. Go to the ``View`` tab.

#. Select the ``Category template``, in this case ``Category with products``, which displays the products assigned
   to the category.

#. Click ``Save View Settings``.

Add Products
============

#. Go to ``Catalog / Products`` and click ``Create Your First Product``.

#. Enter a ``Name`` and a ``Slug`` and click ``Add Product``. The ``Data`` tab of the new product opens.

#. Enter the ``SKU`` of the product. This is the unique id of the product, taken from your ERP for instance.

#. Enter the ``Price`` and select the ``Tax``.

#. Enter a ``Short description``. It is displayed in overviews, e.g. when a category lists its products.

#. Enter a ``Description``. It is displayed on the page of the product.

#. Check ``Active``. Only active products are displayed to customers.

#. Click ``Save Product Data``.

#. Go to the ``Categories`` tab, select the category from above, and click ``Save Categories``.

#. Go to the ``Images`` tab, choose the images of the product, and click ``Upload images``.

#. Click ``View Product`` to see the product in the shop.

Set the Currency
================

The currency is a setting of the project, the default is ``EUR``::

    LFS_CURRENCY = "USD"

What's Next?
============

* Add more categories and products.

* :ref:`Add accessories to your products <products_management_accessories>`.

* :ref:`Add related products to your products <products_management_related_products>`.

* :doc:`Add variants </user/howtos/how_to_variants>`.

* :doc:`Manage taxes </user/management/shop/product_taxes>`.

* :doc:`Manage shipping methods </user/howtos/how_to_shipping_method>`.

* :doc:`Manage payment methods </user/howtos/how_to_payment_method>`.

* :doc:`Manage delivery times </user/management/shop/delivery_times>`.

* :ref:`Manage stock information <products_management_stock>`.

* Edit the pages ``Terms and Conditions`` and ``Imprint`` under ``HTML / Pages`` before the shop goes live.
