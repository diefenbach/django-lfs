.. _getting_started:

===============
Getting Started
===============

This document explains the first steps after the shop has been installed. For
installation please refer to :doc:`/introduction/installation`.

.. include:: /includes/demo_shop.rst

Enter Basic Information
=======================

At first you should go to the shop's preferences and enter basic information.
For that please

1. Visit http://localhost:8000/manage.

2. Login if your aren't yet.

3. Browse to ``Shop / Preferences``.

Go to the ``Shop`` tab.

1. Enter a ``Name``. This is the name of the shop, for instance ``ACME Inc``.
   It is used on several places, e.g. as the title of all HTML pages.

2. Enter the ``Shop owner``. This is the full name of the shop owner, e.g.
   John Doe.

3. Enter ``From e-mail address``. This e-mail address is used as sender
   for all e-mails which are sent from the shop, e.g. the order has been
   received message to the shop customer.

4. Enter ``Notification e-mail addresses``. To this addresses all notification
   messages will be sent. For example if an order has been submitted.

Go to the ``Default Values`` tab.

1. Select the default ``Price Calculator``. This will be use for all products
   if they don't overwrite it explicitly.

2. Select ``Invoice Countries`` and ``Shipping Countries``. All selected
   countries will be available to the shop customers for selection.

3. Select ``Default Country``. This country will be preselected as default
   country.

Add Taxes
=========

1. Go to ``Shop / Product Taxes``

2. As there are no taxes yet, you are redirected automatically to the ``Add
   tax`` tab.

3. Enter the ``Rate`` (in percentage), for instance 19.0.

4. Enter the ``Description``. This is just for internal purposes.

5. Click on ``Add tax``.

6. You can add more taxes by clicking on *Add tax* and executing steps 2. to
   4.

Add Delivery Times
==================

Delivery times are used for shipping methods and/or single products. The
delivery for a whole cart is calculated on base of the selected products and the
shipping method and their assigned delivery times.

1. Go to ``Shop / Delivery times``

2. As there are no delivery times yet, your are redirected automatically to the
   *Add delivery time* form.

3. Enter ``Min``, the minimal delivery time.

4. Enter ``Max``, the maximal delivery time.

5. Enter the ``Unit`` of this delivery time.

6. Enter the ``Description``. This is just for internal purposes.

7. Click on ``Add delivery time``

8. You can add more delivery times by clicking on ``Add delivery time`` and
   executing steps 3. - 7.

Enter Categories and Products
=============================

Now go to ``Catalog / Categories`` and add a new category. Since there are no
categories yet, you will be redirected automatically to the add form.

1. Enter ``name`` and a ``slug``. You will see, that the slug is filled
   automatically but you can change it of course.

2. Enter a ``short description``. This will be displayed when the category is
   displayed within a overview, e.g. when a category displays is sub
   categories.

3. Enter a ``description``. This will be displayed within the detail view of
   a category.

4. Select the ``Category template``, this is ``Category with products``, which
   means the assigned products of the category will be displayed or ``Category
   with sub categories``, which means the sub categories of the category will be
   display).

5. Now save the category.

Now go to ``Catalog / Products`` and add a new Product. Since there is no
product yet, you will redirected automatically to the add form.

1. Enter ``name`` and a ``slug``. You will see, that the slug is filled
   automatically but you can change it of course.

2. Click ``Add Product``.

Now you can add more data to your product. Go to the ``Data`` tab

1. Enter the ``SKU`` of the product. This is the unique id of the product - taken
   from your ERP for instance.

2. Enter the ``price`` of the product.

3. Enter a ``Short Description``. This will be displayed when the product is
   displayed within a overview, e.g. when a category displays it's assigned
   products.

4. Enter a ``description``. This will be displayed within the detail view of
   a product.

5. Click on ``Save Data``.

Go to the ``Categories`` tab

1. Select the above entered category and click ``Save Categories``.

Go to the ``Images`` tab

1. Click ``Select Images``, browse to your images and select all images you want
   to upload. You will see an upload indicator and all images will be uploaded.

Go back to the ``Product`` tab

1. Check the ``Active`` check box. Only active products are displayed to the
   customers.

2. Click ``Save data``.

3. Click on ``Goto Product`` to visit the new product.

Set Default Locale and Currency
===============================

``Default locale`` and ``currency`` can be set through the :term:`LMI` in
``Shop / Default values`` e.g. for American dollars you should set your locale
to ``en_US.utf8``.

You may have to install this locale on your server PC for this to work, to check
what locales you currently have installed open a terminal and type::

    locale -a

To install an english locale (on Debian/Ubuntu)::

    sudo apt-get install language-support-en


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

* Add some portlets to your shop and/or categories.
