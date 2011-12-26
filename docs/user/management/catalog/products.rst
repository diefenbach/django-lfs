.. index:: Product, Price Calculator

.. _products_management:

========
Products
========

This section describes the product management interface.

.. _products_management_site_actions:

Site actions
============

Add product
    Adds a product to the catalog.

Delete product
    Deletes the current displayed product.

View product
    Opens the product in a pop-up window to quickly check the appearance of
    the product without leaving the :term:`LMI`.

Goto product
    Leaves the :term:`LMI` and goes to customer view of the current displayed
    product.

Product type
    Select box to change the :ref:`type of the product <product-types-label>`.

.. _products_management_tabs:

Tabs
====

In this section we will go through all tabs and fields of the product
management interface.

.. _products_management_data:

Data
----

This tab contains the core data of the product.

Active
    Only active products are displayed to the customer, can be found, bought
    etc.

Name
    The name of the product. This is displayed on the title of the product
    page, within overviews and as part of the HTML meta title tag.

Slug
    The last part of the product's URL. This must be unique.

Redirect to
    If this field is not empty the visitor is redirected to the given URL. This
    might be useful if your product has been indexed by search engines (like
    Google).

SKU
    Your unique product id.

SKU Manufacturer
    The unique product id of the manufacturer (external SKU).

Price
    The price of the product. Whether this price is considered net or gross
    dependents on the selected price calculator for this product (see
    below).

Tax
    The tax rate of the product. Whether this is included or excluded
    dependents on the selected price calculator for this product (see
    below).

Price Calculator
    Determines how a products price is calculated using the products price
    and tax stored in the database. If you leave this field blank, your
    pricing calculator will default to the shop :ref:`price calculator <shop-price-calculator-label>`.

    LFS ships with two pricing calculator methods:

    * Price Includes Tax
        Your product price in the database includes tax.

    * Price Excludes Tax
        Your product price in the database excludes tax.

For sale
    If the checkbox is activated the entered ``for sale price`` is active
    for this product. On all views the price is displayed stroked and the
    for sale price is also displayed for the product.

Unit
    The unit of the product. This is displayed after the price of the product.

Price unit
    The price unit of the product. This is displayed before the quantity field
    of the product.

Type of quantity field
    There are three types of quantity fields at the moment:

    Integer
        The quantity must be an integer. All decimal places are ignored.

    Decimal 0.1
        The quantity must be a decimal number with one place. More decimal
        places are ignored.

    Decimal 0.01
        The quantity must be a decimal number with two places. More decimal
        places are ignored.

Short description
    A short description of the product. This is displayed within overviews
    like categories or the search result page.

Description
    The detailed description of the product. This is displayed within the
    product page.

.. index:: Static Block

Static block
    An optional static block which displayed on top of the product view.

.. index:: Template

Product template
    The selected product template decides how the content of the product is
    structured.

.. _products_management_categories:

Categories
----------

Within this tab you can assign categories to the product. To do that just
select all categories the product should be a part of and click on *Save
categories*.

.. Note::

    You can also :doc:`assign products to categories </user/management/catalog/categories>`.

.. _product-images-label:

Images
------

Within this tab you can add images to the product.

Images are displayed on the details view of the product. The first image
is the default image of the product and is also displayed on overviews like
the category view or search result view.

Add images
    Click on the *Select images* button and select as many images as you want
    within your browsers pop-up window. You can use shift click to select a
    range of images at once and ctrl (cmd for apple users) click to select
    more images. Now click on open to start the upload process. You will now
    see a progress bar meanwhile your images are being uploaded.

Update images
    To update the images just change the Title and/or the position of all
    products you want to change and click on the *Update* button.

Move images
    To move images just click on the up or down arrow beside the image.

Delete images
    To delete images select the checkboxes beside all images you want to delete
    and click the *Delete* button.

.. _products_management_attachements:

Attachments
------------

Within this tab you can add attachments to the product.

Attachments are displayed for download on the details page of the product.

Add attachments
    Click on the *Select files* button and select as many attachments as you
    want within your browsers pop-up window. You can use shift click to select
    a range of images at once and ctrl (cmd for apple users) click to select
    more images. Click on select to start the upload process. You will now
    see a progress indicator meanwhile your images are being uploaded.

Update attachments
    To update the images just change the Title and/or the position of all
    products you want to change and click on the *Update* button.

Move attachments
    To move attachments you just click on the up or down arrows beside the
    attachment.

Delete attachments
    To delete attachments select the checkboxes beside all images you want to
    delete and click the *Delete* button.

.. _products_management_accessories:

Accessories
-----------

Within this tab you can manage the accessories of this product.

Add Accessories
^^^^^^^^^^^^^^^

Within the ``Selectable Products`` section select all checkbox beside the
product you want to add as accessory to the product and click on ``Add To
Accessories``.

.. Note::

    You can filter the selectable products by name and category with the
    input fields on top of the ``Selectable Products`` section.

Update accessories
^^^^^^^^^^^^^^^^^^

Within the ``Selected Products`` section change the values you want and click
on ``Save accessories``.

Position
    The position within the product. Lower numbers are displayed first.

Quantity
    The entered quantity is displayed next to the accessory. The shop customer
    can only add the given quantity to the cart.

Remove accessories
^^^^^^^^^^^^^^^^^^

Within the ``Selected Products`` section select all checkboxes beside the
products you want to remove from the product and click on ``Remove From
Accessories``.

.. _products_management_related_products:

Related products
----------------

Within this tab you can manage the related products of this product.

Add Related Products
^^^^^^^^^^^^^^^^^^^^

Within the ``Selectable Products`` section select all checkbox beside the
product you want to add as related products to the product and click on
``Add To Related Products``.

.. Note::

    You can filter the selectable products by name and category with the
    input fields on top of the ``Selectable Products`` section.

Remove Related Products
^^^^^^^^^^^^^^^^^^^^^^^

Within the ``Selected Products`` section select all checkboxes beside the
products you want to remove from the product and click on ``Remove From
Related Prouducts``.

.. _products_management_stock:

Stock
-----

Within this tab you can manage all stock related information of the product,
like the dimension, stock amount and delivery dates.

Dimension
^^^^^^^^^

The values of the product which are considered shipping relevant, i.e. the
product within its package.

Weight
    The weight of the product.

Height
    The height of the product.

Width
    The width of the product.

Length
    The length of the product.

Stock data
^^^^^^^^^^

Deliverable
    If this is deactivated the product is not deliverable at all. The shop
    customer sees the product but he is not able to add the product to the
    cart.

Manual delivery time
    By default the delivery time is calculated automatically by the valid
    shipping method for this product. With this field the shop owner can
    overwrite this behavior and can put in a manual delivery time.

Manage Stock amount
    If this is checked the stock amount will be decreased when the product
    has been bought. Additionally the maximum amount which can be bought is
    the number in ``Stock amount`` (see below).

Stock amount
    The available amount of the product in stock.

Order time
    Duration from ordering the product to being in stock again (when it is out
    of stock).

Ordered at
    The date when the **shop owner** has ordered the product.

.. note::

    If ``Order time`` and ``Order at`` is given the total ``delivery time`` is
    calculated based on this two fields and the default ``Delivery time``.

Packaging Unit
^^^^^^^^^^^^^^

Active packing unit
    If this is checked the product can only be sold in packages.

Packing unit
    Amount of products per package.

Unit:
    The unit of the package, for instance ``package`` or ``set``.

.. index:: SEO

.. _products_management_seo:

SEO
---

This tab is used to optimize your product for search engines. You can enter data
for all usual HTML meta data fields. However LFS provides some reasonable default
values for all fields.

Meta title
    This is displayed within the meta title tag of the category's HTML tags. By
    default the name of the product is used.

Meta keywords
    This is displayed within the meta keywords tag of the category's HTML page.
    By default the short description of the category is used.

Meta description
    This is displayed within the meta description tag of the category's HTML
    page. By default the short description of the category is used.

You can use several placeholders within the above mentioned fields:

<name>
    The name of the product.

<short-description>
    The short description of the product (only within meta keywords/description-field).

.. index:: Portlets

.. _products_management_portlets:

Portlets
--------

This tab is used to assign :term:`portlets` to the product.

Blocked parent slots
    By default portlets are inherited from the current category. To block
    portlets check the regarding slots and click on the ``Save blocked parent
    slots`` button.

Slots
    Here you can see all directly assigned portlets to the product. In order
    to edit a portlet click on row of the portlet. In order to delete a
    portlet click on the red cross beside the portlet. You can also change
    the position of the portlets by clicking on the up and down arrows beside
    the portlets.

Add new Portlet
    In order to add a portlet to the product select the type of portlet and
    click on ``Add portlet``.

.. _products_management_properties:

Properties
----------

This tab is used to assign properties to the product (via property groups)
and add values to them.

To do that proceed as following:

1. Select the ``Property groups`` you want to assign to the product and click
   on ``Update property groups``.

2. Enter the values for the properties you want and click on ``Update
   properties``.

Dependent on the kind of the property you can add values for the default
value, the filter value and/or the displayed value.

See also
========

* :ref:`Products in general <products_concepts>`
* :ref:`Portlets in general <portlets_concepts>`
* :ref:`Properties in general <properties_concepts>`
