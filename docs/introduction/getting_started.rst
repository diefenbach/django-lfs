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

#. Login, if you aren't yet.

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

#. Click on the ``Save Shop`` button.

#. Go to the ``Default Values`` tab.

#. Select the default ``Price Calculator:``. This is the default for all
   products, if the price calculator is not explicitly selected on a product.

#. Select ``Invoice Countries`` and ``Shipping Countries``. All selected
   countries will be available to the shop customers for selection.

#. Select ``Default Country``. This country will be preselected as default
   country.

#. Click on the ``Save Default Values`` button.

Add Product Taxes
=================

#. Go to ``Shop / Product Taxes`` and click on the ``Add Product Tax`` button.

#. Enter the ``Rate`` (in percentage), for instance 19.0.

#. Click on the ``Add Tax`` button.

#. You can add more taxes by clicking on the ``Add Product Tax`` site action
   and executing steps 2 to 3.

Add Delivery Times
==================

#. Go to ``Shop / Delivery Times`` and click on the ``Add Delivery Time``
   button.

#. Enter ``Min``, the minimal delivery time.

#. Enter ``Max``, the maximal delivery time.

#. Enter the ``Unit`` of this delivery time.

#. Click on the ``Add Delivery Time`` button.

#. You can add more delivery times by clicking on ``Add delivery time`` link and
   executing steps 2 to 3.

Add Categories
==============

#. Now go to ``Catalog / Categories``.

#. Click on the ``Add Category`` button.

#. Enter a ``name`` and a ``slug``.

#. Click on the ``Add Category`` button.

#. Go to the ``Data`` tab.

#. Enter a ``Description``. This will be displayed within the detail view of
   a category.

#. Click on the ``Save Data`` button.

#. Go to the ``View`` tab.

#. Select the ``Category Template``, In this case ``Category with Products``
   which means the assigned products of the category will be displayed.

#. Click on the ``Save View`` button.

Add Products
============

#. Now go to ``Catalog / Products`` and click on the ``Add Product`` button.

#. Enter ``name`` and a ``slug``.

#. Click on the ``Add Product`` button.

#. Go to the ``Data`` tab

#. Enter the ``SKU`` of the product. This is the unique id of the product - taken
   from your ERP for instance.

#. Enter the ``Price`` of the product.

#. Enter a ``Short Description``. This will be displayed when the product is
   displayed within a overview, e.g. when a category displays it's assigned
   products.

#. Enter a ``Description``. This will be displayed within the detail view of
   a product.

#. Click on the ``Save Data`` button.

#. Go to the ``Categories`` tab

#. Select the above entered category and click ``Save Categories``.

#. Go to the ``Images`` tab

#. Click ``Choose Files``, browse to your images and select all images you want
   to upload. You will see an upload indicator and all images will be uploaded.

#. Go back to the ``Data`` tab

#. Check the ``Active`` check box. Only active products are displayed to the
   customers.

#. Click on the ``Save Data`` button.

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

.. Note::

   After you have changed the locale you need to restart your instance to make it
   active.

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
