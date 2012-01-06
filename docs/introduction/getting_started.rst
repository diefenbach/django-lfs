.. _getting_started:

===============
Getting Started
===============

This document explains the first steps after the shop has been installed. For
the installation process please refer to :doc:`/introduction/installation`. If
you want to know more about single data fields within the forms below, you can
just click on the ``Help`` menu, which opens the context aware help.

.. include:: /includes/demo_shop.rst

Enter Shop Preferences
======================

#. Browse http://localhost:8000/manage.

#. Login, if your aren't yet.

#. Browse to ``Shop / Preferences``.

#. Go to the ``Shop`` tab.

#. Enter the ``Name``. This is the name of the shop, for instance ``ACME Inc``
   which is used on several places, e.g. as part of the meta title of all HTML
   pages.

#. Enter the ``Shop Owner``. This is the full name of the shop owner.

#. Enter ``From E-mail Address``. This e-mail address is used as sender for all
   e-mails which are sent from the shop, e.g. the order confirmation mail to the
   shop customer.

#. Enter ``Notification E-Mail Addresses``. To this addresses all notification
   messages will be sent. For example, if an order has been submitted.

#. Go to the ``Default Values`` tab.

#. Select the default ``Price Type``. This is the default for all products, if
   the price type is not explicitly selected on a product.

#. Select ``Invoice Countries`` and ``Shipping Countries``. All selected
   countries will be available to the shop customers for selection.

#. Select ``Default Country``. This country will be preselected as default
   country.

Add Product Taxes
=================

#. Go to ``Shop / Product Taxes``. As there are no taxes yet, you are redirected
   automatically to the  form.

#. Enter the ``Rate`` (in percentage), for instance 19.0.

#. Click on ``Add Tax`` button.

#. You can add more taxes by clicking on the ``Add Product Tax`` site action
   and executing steps 2 to 3.

Add Delivery Times
==================

#. Go to ``Shop / Delivery Times``. As there are no delivery times yet, your are
   redirected automatically to the add form.

#. Enter ``Min``, the minimal delivery time.

#. Enter ``Max``, the maximal delivery time.

#. Enter the ``Unit`` of this delivery time.

#. Enter the ``Description``. This is just for internal purposes.

#. Click on ``Add delivery time`` button.

#. You can add more delivery times by clicking on ``Add delivery time`` link and
   executing steps 2 to 4.

Add Categories
==============

#. Now go to ``Catalog / Categories``.

#. Click on ``Add Category``.

#. Enter a ``name`` and a ``slug``.

#. Click on the ``Add Category`` button.

#. Go to the ``Data`` tab.

#. Enter a ``Description``. This will be displayed within the detail view of
   a category.

#. Go to the ``View`` tab.

#. Select the ``Category Template``, In this case ``Category with Products``
   which means the assigned products of the category will be displayed.

#. Click on the ``Save View`` button.

Add Products
============

#. Now go to ``Catalog / Products`` and add a new Product. Since there is no
   product yet, you will redirected automatically to the add form.

#. Enter ``name`` and a ``slug``.

#. Click on the ``Add Product`` button.

#. Go to the ``Data`` tab

#. Enter the ``SKU`` of the product. This is the unique id of the product - taken
   from your ERP for instance.

#. Enter the ``Price`` of the product.

#. Enter a ``Short Description``. This will be displayed when the product is
   displayed within a overview, e.g. when a category displays it's assigned
   products.

#. Enter a ``description``. This will be displayed within the detail view of
   a product.

#. Click on ``Save Data``.

#. Go to the ``Categories`` tab

#. Select the above entered category and click ``Save Categories``.

#. Go to the ``Images`` tab

#. Click ``Select Images``, browse to your images and select all images you want
   to upload. You will see an upload indicator and all images will be uploaded.

#. Go back to the ``Product`` tab

#. Check the ``Active`` check box. Only active products are displayed to the
   customers.

#. Click ``Save data``.

#. Click on ``Goto Product`` to visit the new product.

Set Default Locale and Currency
===============================

Go to ``Shop / Preferences / Default Values`` and enter the locale
``en_US.utf8``. This will activate the US Dollars at the same time.

Usually there are several locale installed on your computer. In order to check
which ones, please open a terminal and type::

    locale -a

To install an english locale (on Debian/Ubuntu) please enter::

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
