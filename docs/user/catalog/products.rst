========
Products
========

Overview
========

* Products are sold to the shop customer.
* Products can belong to an arbitrary amount of categories.
* Products can have an arbitrary amount of images.
* Products can have portlet

.. _product-types-label:

Types
=====

There are three types of products: ``product``, ``product with variants`` and 
``variant``. There are further described in more detail.

.. _product-product-label:

Product
-------

This is the default product of LFS. Just enter the appropriate data, set it
to active and the product is ready for sale.

.. _product-configurable-product-label:

Configurable product
--------------------

* A configurable product is a product with several properties
* Properties can be a selection or a input field
* Properties can be price changing
* The price of an configurable product is usually calculated by the product's 
  base price plus all selected/entered values of its properties

.. _product-product-with-variant-label:

Product with variants
---------------------

A product with variants consists of two parts: The ``product with variant``
which is the parent of a ``variant``.

The parent can't be sold. It is just a container for the variants and provides
default data which can be inherited by the variants.

The parent has/defines some ``properties`` (global or local) which are the base
to create the ``variants``.

.. _product-variant-label:

Variant
-------

This is a single variant of a ``Product with variants``.

* A variant can be sold to the customer.

* By default a variant inherits all data of the related ``Product with
  variants``.

* A variant can overwrite the data from the belonging parent product. To do
  that the fields in question have to be activated explicitly.

* A variant belongs to a unique combination of properties. The properties are
  defined by the ``Product with variants``.

.. _product-tabs-label:

Tabs
====

In this section we will go through all tabs and fields of the product
management interface.

.. _product-data-label:

Data
----

This tab contains the core date of the product.

Active
    Only active products are displayed to the customer, can be found, bought
    etc.

Redirect to
    If this field is not empty the visitor is redirected to the given URL. This
    might be useful if your product has been indexed by search engines (like
    Google).

Name
    The name of the product. This is displayed on the title of the product
    page, within overviews and as part of the HTML meta title tag.

slug
    The part of the product's URL. This must be unique.

SKU
    Your unique product id.

SKU manufacturer
    The unique product id of the manufacturer (the external SKU)

Price
    The gross price of the product

Tax
    The percentage tax of the product. Note: Taxes are managed central within
    Shop / Taxes.

Price Calculator
    Determines how a products price is calculated using the products price and tax stored in the database.
    If you leave this field blank, your pricing calculator will default to lfs.core.settings.LFS_DEFAULT_PRICING_CALCULATOR

    LFS ships with two pricing calculator methods:

    * Price Includes Tax
        Your product price in the database includes tax, use this calculator if you are only shipping to one country
        and you don't want your displayed prices to vary when tax rates change.

    * Price Excludes Tax
        Your product price in the database excludes tax, use this calculator if you are shipping to multiple countries
        and you want your total price to vary with tax rate changes.

    You can also add :doc:`custom pricing calculators </developer/howtos/how_to_add_product_pricing>`.


For sale
    If this is activated the default price of the product is stroked and
    the for entered for sale price is displayed.

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
    The selected product template decides how the content of the page is
    structured. By default there is only one template. Developers can add
    more templates easily (:doc:`see here for more </developer/howtos/how_to_add_own_templates>`).

.. _product-categories-label:

Categories
----------

Within this tab you can assign categories to the product. To do that just
select all categories the product should be a part of and click on ``Save
categories``.

There are three helper links on top of the category tree:

Collapse all
    This will collapse the whole category tree

Expand all
    This will expand the whole category tree

Show selected
    This will collapse all category which are currently selected.

Please note: you can also assign products to categories
(:doc:`see here for more </user/catalog/categories>`).

.. _product-images-label:

Images
------

Within this tab you can add images to the product.

Add images
    Click on the ``Add images`` button and select as many images as you want
    within your browsers popup window. You can use shift click to select a
    range of images at once and ctrl (cmd for apple users) click to select
    more images. Now click on open to start the upload process. You will now
    see a progress bar meanwhile your images are being uploaded.

Update images
    To update the images just change the Title and/or the position of all
    products you want to change and click on the ``Update`` button.

Delete images
    To delete images select the checkbox beside all images you want to delete
    and click the ``Delete`` button.

.. _product-accessories-label:

Accessories
-----------

Within this tab you can manage the accessories of this product.

Accessories are displayed within the ``Added to cart`` view (the view is
displayed after a shop customer has added product to the cart) in order to
offer them to be also added to the cart.

**Generally**

* Accessories are not bidirectional. You need to assign accessories on every
  product.
  to enter the related products on each side of the relation.
* Optionally you can filter the available products with the text (name) and
  select box (categories) on top of the page.
* You can also navigate through the available products by clicking on the
  ``First``, ``Previous``, ``Next``, ``Last`` links.

*Add accessories**

1. Select all checkbox beside the products you want to add as accessory to
   the product

2. Click on ``Add to accessories``

You will now see the above selected products within the ``Accessories``
section and removed from the ``Products`` section.

**Update accessories**

To update assigned accessories just change the values you want within the ``
Accessories`` section and click on ``Save accessories```.`

Position
    The position within the product

Quantity
    The entered quantity is displayed next to the accessory. The shop customer
    can only add the given quantity to the cart.

**Remove accessories**

1. Within the ``accessories`` section select all checkboxes beside the products
   you want to remove from the product.

2. Click on ``Remove from accessories``.

You will now see the above selected products within the ``Products``
section and removed from the ``Accessories`` section.

.. _product-related-products-label:

Related products
----------------

Within this tab you can add related products to the product.

Related can be displayed within a :term:`portlet`. Related products are
similar to the current displayed product.

**Generally**

* Related products are not bidirectional. If you to want them to be you need
  to enter the related products on each side of the relation.
* Optionally you can filter the available products with the text (name) and
  select box (categories) on top of the page.
* You can also navigate through the available products by clicking on the
  ``First``, ``Previous``, ``Next``, ``Last`` links.

**Add related products**

1. Select all checkbox beside the products you want to add as related product
   to the product

2. Click on ``Add to accessories``

You will now see the above selected products within the ``Accessories``
section and removed from the ``Products`` section.

**Update accessories**

To update assigned accessories just change the values of the assigned accessories
you want (within the ``Accessories`` section) and click on ``Save accessories``.

    Position
        The position within the product

    Quantity
        The entered quantity is displayed next to the accessory. The shop customer
        can only add the given quantity to the cart.

**Remove accessories**

1. Within the ``accessories`` section select all checkboxes beside the products
   you want to remove from the product.

2. Click on ``Remove from accessories``.

You will now see the above selected products within the ``Products``
section and removed from the ``Accessories`` section.

.. _product-stock-label:

Stock
-----

Within this tab you can manage all stock related information of the product,
like the dimension, stock amount and delivery dates.

**Dimension**

The values of the product are considered shipping relevant, e.g. the product
within the package:

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

If ``Order time`` and ``Order at`` is given LFS calculates the ``delivery
time`` for the shop customer based on this and the default ``delivery time``.

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

    **<name>**

    The name of the product.

    **<short-description>**

    The short description of the product (only within meta
    keywords/description-field).

.. _product-portlets-label:

Portlets
--------

The tab is used to assign :term:`portlets` to the product.

**Overview**

By default portlets are inherited from the current category.

**Block portlets**

Portlets can be blocked by :term:`slots`. To block portlets activate the appropriate
checkbox within the ``Blocked parent slots`` section and click on the ``Save
blocked parent slots``.

**Add portlets**

In order to add a new portlet to the category select the type of the portlet you
want to add, click ``Add portlet``, fill in the form and click on ``Save
portlet`` button.

**Edit portlets**

In order to edit a portlet click on the ``edit`` link beside the portlet, enter
your data and click on ``Save portlet`` button.

**Delete portlets**

In order to delete a portlet click on the ``delete`` link beside the portlet and
click on ``yes``.

.. _product-properties-label:

Properties
----------

Within this tab you can assign property groups to the product and add values
to the single properties. For more about properties, please see here:
:doc:`Properties </user/misc/properties>`.

To add properties and property values to the product proceed as following:

1. Select the ``Property groups`` you want to assign to the product and click
   ``Update property groups``.

You will now see all properties which are assigned to the product. 

2. Enter the values for every assigned property and click on ``Update
   properties``

Dependend on the kind of the property you can add values for the default value,
the filter value and the displayed value.