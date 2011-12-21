Getting started
===============

This document explains the first steps after the shop has been installed. For
installation please refer to :doc:`/introduction/installation`.

Enter basic information
-----------------------

At first you should go to the shop's preferences and enter basic information.
For that please

   * Visit http://localhost:8000/manage
   * Login
   * Browse to *Shop / Preferences*

Go to the *Shop* tab.

   * Enter a *Name*. This is the name of the shop, for instance *ACME Inc*.
     It is used on several places, e.g. as the title of all HTML pages.

   * Enter the *Shop owner*. This is the full name of the shop owner, e.g.
     *John Doe*.

   * Enter *From e-mail address*. This e-mail address is used as sender
     for all e-mails which are sent from the shop, e.g. the order has been
     received message to the shop customer.

   * Enter *Notification e-mail addresses*. To this addresses all notification
     messages will be sent. For example if an order has been submitted.

Go to the *Default Values* tab.

   * Select the default *Price Calculator*. This will be use for all products
     if they don't overwrite it explicitly.

   * Select *Invoice Countries* and *Shipping Countries*. All selected
     countries will be available to the shop customers for selection.

   * Select *Default Country*. This country will be preselected as default
     country.

Add taxes
---------

1. Go to *Shop* / *Product Taxes*
2. As there are no taxes yet, you are redirected automatically to the *Add
   tax* tab.
3. Enter the *Rate* (in percentage), for instance 19.0,
4. Enter the *Description*. This is just for internal purposes.
5. Click on *Add tax*
6. You can add more taxes by clicking on *Add tax* and executing steps 2. to
   4.

Add delivery times
------------------

Delivery times are used for shipping methods and/or single products. The
delivery for a whole cart is calculated on base of the selected products and
the shipping method and their assigned delivery times.

1. Go to *Shop* / *Delivery times*
2. As there are no delivery times yet, your are redirected automatically to the
   *Add delivery time* form.
3. Enter *Min*, the minimal delivery time.
4. Enter *Max*, the maximal delivery time.
5. Enter the *Unit* of this delivery time.
6. Enter the *Description*. This is just for internal purposes.
7. Click on *Add delivery time*
8. You can add more delivery times by clicking on *Add delivery time* and
   executing steps 3. - 7.

Enter categories and products
-----------------------------

Now go to *Catalog / Categories* and add a new category.

Since there are no categories yet, you will be redirected automatically to the
add form.

   * Enter *name* and a *slug* (you will see, that the slug is filled
     automatically but you can change it of course)

   * Enter a *short description*. This will be displayed when the category is
     displayed within a overview, e.g. when a category displays is sub
     categories

   * Enter a *description*. This will be displayed within the detail view of
     a category.

   * Select the *Category template*, this is *Category with products* (the
     assigned products of the category will be displayed), *Category with
     sub categories* (the sub categories of the category will be display) or
     *Description only* (only the description field will be displayed).

   * Now save the category

Now go to *Catalog / Products* and add a new Product.

Since there is no product yet, you will redirected automatically to the add
form.

   * Enter *name* and a *slug* (you will see, that the slug is filled
     automatically but you can change it of course)

   * Enter the *SKU* of the product. This is the unique external id of the
     product - taken from your ERP for instance

   * Enter the *price* of the product

   * Click *Add product*

Now you can add more data to your product:

Go to the *Product* tab

   * Enter a *short description*. This will be displayed when the product is
     displayed within a overview, e.g. when a category displays it's assigned
     products.

   * Enter a *description*. This will be displayed within the detail view of
     a product.

   * Enter the price of the product.

   * Click *Save data*

Go to the *Categories* tab

   * Select the above entered category and click *Save categories*.

Go to the *Images* tab

   * Click *Select images* browse to your images and select all images you
     want to upload.

Go back to the *Product* tab

   * Check the *Active* check box. Only active products will be displayed to
     the customers.

   * Click *Save data*

   * Click on *View product* to view your new product.


Set default locale and currency
-------------------------------

Default locale and currency can be set through the :term:`LMI` in *Shop /
Default values* e.g. for American dollars you should set your locale to
*en_US.utf8*

You may have to install this locale on your server PC for this to work,
to check what locales you currently have installed open a terminal and type::

    locale -a

To install an english locale (on Debian/Ubuntu)::

    sudo apt-get install language-support-en


What's next?
------------

Now you can:

   * add more categories and products
   * :ref:`add accessories to your products <product-accessories-label>`
   * :ref:`add related products to your products <product-related-products-label>`
   * :doc:`add variants </user/howtos/how_to_variants>`
   * :doc:`manage taxes </user/misc/taxes>`
   * :doc:`manage shipping methods </user/howtos/how_to_shipping_method>`
   * :doc:`manage payment methods </user/howtos/how_to_payment_method>`
   * :doc:`manage delivery times </user/shop/delivery_times>`
   * :ref:`manage stock information <product-stock-label>`
   * Add some portlets to your shop and/or categories
