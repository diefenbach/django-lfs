========
Products
========

This sections describes the products management interface.

.. _product-site-actions-label:

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

.. _product-tabs-label:

Tabs
====

In this section we will go through all tabs and fields of the product
management interface.

.. _product-data-label:

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

    .. Note::

        Taxes are managed central within :doc:`Shop / Taxes </user/shop/taxes>`.

Price Calculator
    Determines how a products price is calculated using the products price
    and tax stored in the database. If you leave this field blank, your
    pricing calculator will default to the shop :ref:`price calculator <shop-price-calculator-label>`.

    LFS ships with two pricing calculator methods:

    * Price Includes Tax
        Your product price in the database includes tax.

    * Price Excludes Tax
        Your product price in the database excludes tax.

    .. Note::

        You can also add :doc:`custom pricing calculators </developer/howtos/how_to_add_product_pricing>`.

For sale
    If the checkbox is activated the entered ``for sale price`` is active
    for this product. On all views the price is displayed stroked and the
    for sale price is also displayed for the product.

Unit
    The unit of the product. This is display after the price of the product.

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

Static block
    A :term:`Static Block`. This is displayed on top of the product page. Note:
    static blocks are managed central within HTML / Static blocks.

.. index:: Template

Product template
    The selected product template decides how the content of the product is
    structured.

.. _product-categories-label:

Categories
----------

Within this tab you can assign categories to the product. To do that just
select all categories the product should be a part of and click on *Save
categories*.

.. Note::

    You can also :doc:`assign products to categories </user/catalog/categories>`.

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

.. _product-attachments-label:

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

.. _product-accessories-label:

Accessories
-----------

Within this tab you can manage the accessories of this product.

Accessories are displayed within the *Added to cart* view (the view is
displayed after a shop customer has added a product to the cart) in order to
offer them to be also added to the cart.

**Generally**

* Accessories are not bidirectional. You need to enter the accessories on
  each side of the relation.

**Add accessories**

1. Select all checkbox beside the selectable products you want to add as
   accessory to the product. **Note:**

   .. Note::

        You can filter the selectable products by name and category with the
        input fields on top of the selected products section.

2. Click on *Add to accessories*

You will now see the above selected products within the *Selected products*
section and removed from the *Products* section.

**Update accessories**

To update assigned accessories just change the values you want within the
*Selected products* section and click on *Save accessories*.

Position
    The position within the product.

Quantity
    The entered quantity is displayed next to the accessory. The shop customer
    can only add the given quantity to the cart.

**Remove accessories**

1. Within the *accessories* section select all checkboxes beside the products
   you want to remove from the product.

2. Click on Remove from accessories.

You will now see the above selected products within the *Selectable products*
section and removed from the *Selected products* section.

.. _product-related-products-label:

Related products
----------------

Within this tab you can add related products to the product.

**Generally**

* Related product can be displayed within a :term:`portlet`.

* Related products are not bidirectional. You need to enter the related
  products on each side of the relation.

* Optionally you can filter the selectable products with the text (name) and
  select box (categories) on top of the page.

* You can also navigate through the selectable products by clicking on the
  *First*, *Previous*, *Next*, *Last* links.

**Add to related products**

1. Select all checkbox beside the products you want to add as related product
   to the product

   .. Note::

        You can filter the selectable products by name and category with the
        input fields on top of the selected products section.

2. Click on *Add to related products*

You will now see the above selected products within the *Selected Products*
section and removed from the *Selectable* section.

**Remove related products**

1. Within the *select products* section select all checkboxes beside the
   related products you want to remove from the product.

2. Click on *Remove from related products*.

You will now see the above selected products within the *Selectable products*
section and removed from the *Selected products* section.

.. _product-stock-label:

Stock
-----

Within this tab you can manage all stock related information of the product,
like the dimension, stock amount and delivery dates.

**Dimension**

The values of the product which are considered shipping relevant, e.g. the
product within the package:

Weight
    The weight of the product.

Height
    The height of the product

Width
    The width of the product

Length
    The length of the product

**Stock data**

Deliverable
    If this is deactivated the product is not deliverable at all. The shop
    customer gets a note o the product page and is not able to add the
    product to the cart.

Manual delivery time
    By default the delivery time is calculated by the selected shipping method.
    With this field the shop admin can overwrite this behavior and can put
    in a manual delivery time. For that check the checkbox and select the
    appropriate delivery time from the checkbox.

Manage Stock amount
    If this is checked the stock amount is decreased if a shop customer has
    bought a product.

Stock amount
    The stock amount of the product.

Order time
    The time from ordering a product to delivery

Ordered at
    The date when the shop owner has ordered the product.

If *Order time* and *Order at* is given LFS calculates the *delivery
time* for the shop customer based on this and the default *delivery time*.

**Packaging Unit**

Active packing unit
    If this is checked only packages can be saled for this product. The price
    of is automatically calculated for the amount of pieces/packages.

Packing unit
    Amount of pieces of the product in one package.

Unit:
    The unit of the package, e.g.: package, set, etc.


.. _product-seo-label:

SEO
---

This tab is used to optimize your pages for search engines. You can enter data
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

.. _product-portlets-label:

Portlets
--------

The tab is used to assign :term:`portlets` to the product.

**Overview**

By default portlets are inherited from the current category.

**Block portlets**

Portlets can be blocked by :term:`slots`. To block portlets activate the
appropriate checkbox within the *Blocked parent slots* section and click on
the *Save blocked parent slots*.

**Add portlets**

In order to add a new portlet to the category select the type of the portlet
you want to add, click *Add portlet*, fill in the form and click on *Save
portlet* button.

**Edit portlets**

In order to edit a portlet click on the *edit* link beside the portlet, enter
your data and click on *Save portlet* button.

**Delete portlets**

In order to delete a portlet click on the *delete* link beside the portlet and
click on *yes*.

.. _product-properties-label:

Properties
----------

Within this tab you can assign property groups to the product and add values
to the single properties. For more about properties, please see here:
:doc:`Properties </user/misc/properties>`.

To add properties and property values to the product proceed as following:

1. Select the *Property groups* you want to assign to the product and click
   *Update property groups*.

You will now see all properties which are assigned to the product.

2. Enter the values for every assigned property and click on *Update
   properties*

Dependent on the kind of the property you can add values for the default
value, the filter value and/or the displayed value.

.. seealso::

    * :doc:`Product details </user/misc/products>`
