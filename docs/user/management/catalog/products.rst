.. index:: Product, Price Calculator

.. _products_management:

========
Products
========

This section describes the product management interface (``Catalog / Products``).

.. image:: /images/manage_product_data.png
   :alt: The Data tab of a product, with the product list on the left

On the left is the list of all products, on the right the selected product with its tabs.

Product List
============

Filter
    Shows only products of the selected product type and price calculator. Click ``Apply`` to filter and
    ``Reset`` to show all products again.

Search
    Filters the list by name or SKU.

.. _products_management_site_actions:

Site Actions
============

Add Product
    Opens a dialog to add a product. Select its ``Subtype`` (the :ref:`type of the product <product_types_label>`:
    ``Standard``, ``Product with variants`` or ``Configurable product``), enter its ``Name`` and ``Slug``, and click
    ``Add Product``. The type cannot be changed later.

Delete Product
    Deletes the selected product, after a confirmation.

View Product
    Opens the product in the shop.

.. _products_management_tabs:

Tabs
====

.. _products_management_data:

Data
----

Active
    Only active products are displayed to customers, can be found, and can be bought.

Name
    The name of the product. It is displayed as the title of the product page, in overviews, and as part of the
    meta title.

Slug
    The last part of the product's URL. It must be unique.

SKU
    Your unique product id.

Manufacturer
    The :doc:`manufacturer </user/management/shop/manufacturers>` of the product.

SKU Manufacturer
    The product id of the manufacturer (external SKU).

Price
    The price of the product. Whether it is net or gross depends on the price calculator (see below).

Tax
    The tax rate of the product. Whether it is included in the price or added to it depends on the price
    calculator.

Price calculator
    Determines how the price is calculated from the entered price and tax. Left empty, the product uses the
    :ref:`default price calculator of the shop <preferences_default_values>`.

    LFS ships with two price calculators: ``Price includes tax`` (the entered price includes tax) and ``Price
    excludes tax`` (the entered price excludes tax). Add-ons can add more, for instance lfs-bulk-prices.

For sale / For sale price
    If ``For sale`` is checked, the ``For sale price`` applies. The shop displays the standard price struck
    through and the for sale price emphasized.

Quantity field unit
    Displayed before the quantity field on the product page and after the amount in the cart and in orders.

Type of quantity field
    ``Integer``: the quantity is a whole number, decimal places are ignored. ``Decimal 0.1``: the quantity has one
    decimal place. ``Decimal 0.01``: the quantity has two decimal places.

Active base price
    If checked, the base price of the product is displayed on the product page and in category overviews.

Base price unit
    The unit displayed after the base price.

Base price amount
    The amount used to calculate the base price::

        base price = price / base price amount

Short description
    A short description of the product, displayed in overviews like categories or the search result.

Description
    The detailed description of the product, displayed on the product page.

.. index:: Static Block

Static block
    An optional :ref:`static block <static_blocks_concepts>` displayed on the product page.

.. index:: Template

Product template
    Decides how the content of the product page is structured.

Click ``Save Product Data`` to save the changes.

Configurable products
    Have two more fields:

    Active price calculation
        If checked, the price is calculated with the formula in ``Price Calculation``.

    Price Calculation
        A formula that calculates the price from the values the customer selects for the properties. If the
        formula fails, the product's price is taken.

        .. warning::

            This is an experimental feature. It could be replaced with something different in future.

        The formula is a Python expression with two additional tokens::

            product(<attribute>)
                Refers to the attribute of the current product

            property(<id>)
                Refers to the value of the property with the given <id>

        Example: ``property(15) * product(price)`` multiplies the value of the property with the id 15 with the
        product's price.

Variants
    Have no tax and no quantity fields; they take them from their product. ``Active for sale`` and ``Active base
    price`` have three values: ``Standard`` takes the setting of the product, ``Yes`` and ``No`` set it for the
    variant (then with the for sale price, base price unit and amount of the variant).

.. _products_management_categories:

Categories
----------

Check all categories the product belongs to and click ``Save Categories``.

.. Note::

    You can also :doc:`assign products to a category </user/management/catalog/categories>`.

.. _products_management_images:

Images
------

.. image:: /images/manage_product_images.png
   :alt: The Images tab of a product

The images are displayed on the product page. The first image is the default image of the product, also displayed
in overviews like categories or the search result.

Add images
    Under ``Add images`` choose one or more image files and click ``Upload images``.

Change images
    Change the ``Position``, the ``Title`` or the ``Alt Text`` (the text for screen readers and search engines) and
    click ``Save Changes``. Images with lower positions come first.

Delete images
    Select the images and click ``Delete Selected Images``.

.. _products_management_attachments:

Attachments
-----------

Attachments are files the customer can download on the product page, for instance data sheets.

Add attachments
    Under ``Add attachments`` choose one or more files and click ``Upload attachments``.

Change attachments
    Change the ``Title``, the ``Description`` or the ``Position`` and click ``Save Changes``.

Delete attachments
    Select the attachments and click ``Delete Selected Attachments``.

.. _products_management_properties:

Properties
----------

This tab assigns properties to the product (through property groups) and sets their values.

#. Under ``Select Property Groups`` select the groups of the product (hold Ctrl or Cmd to select several) and click
   ``Update property groups``.

#. Enter the values of the properties and save them. Depending on the property there are up to three kinds of
   values, each with its own button:

   Default values
       The values the product has; saved with ``Update default values``.

   Filter values
       The values used by the filters of the shop; saved with ``Update filter values``.

   Displayed values
       The values displayed on the product page; saved with ``Update displayed values``.

For a product with variants the values of the variant properties are set on the ``Variants`` tab.

.. _products_management_variants:

Variants
--------

This tab manages the variants of a ``Product with variants`` and is only displayed for those.

Local properties
    Properties that belong only to this product. Enter a name and click ``Add property``, then add its options
    (comma separated) with ``Add option``. The properties of the product's property groups (see
    ``Properties``) are offered as well.

    .. note::

        Local properties cannot be used for filtering.

Add Variants
    Select an option for each property, or ``All`` to create a variant for every option, and click ``Add
    variants``. LFS creates a variant for every combination that does not exist yet; it gets the price of the
    product and the product's SKU with a number.

Variants list
    Shows all variants with ``Position``, ``Active``, ``Slug``, ``SKU``, ``Name``, ``Price`` and ``Default`` (the
    variant preselected on the product page). Change the values and click ``Save``; select variants and click
    ``Delete selected`` to delete them. Every other field of a variant is changed on its own page.

Category variant
    Which variant the category overviews display: ``Default`` (the default variant), ``Cheapest price``,
    ``Cheapest base price``, ``Cheapest prices`` (cheapest price and cheapest base price), or a selected variant.
    Click ``Change category variant`` to save.

Display type
    How the product page offers the variants: ``List`` shows all variants in a list, ``Select`` shows a select box
    per property; if the customer selects a combination that does not exist, the shop says so. Click ``Change
    variant display type`` to save.

.. _products_management_accessories:

Accessories
-----------

:ref:`Accessories <marketing_concepts_accessories>` are products that can be bought together with this product.

Add accessories
    In the section ``Products`` (searchable by name and SKU) select the products and click ``Add as Accessories``.

Change accessories
    In the section ``Accessories`` change the ``Position`` (lower numbers come first) and the ``Quantity`` (the
    amount the customer adds to the cart with the accessory) and click ``Save Changes``.

Remove accessories
    In the section ``Accessories`` select the products and click ``Remove Selected``.

.. _products_management_related_products:

Related products
----------------

:ref:`Related products <marketing_concepts_related_products>` are shown to customers who view this product.

Add related products
    In the section ``Products`` select the products and click ``Add as Related``.

Remove related products
    In the section ``Related Products`` select the products and click ``Remove Selected``.

.. _products_management_stock:

Stock
-----

.. image:: /images/manage_product_stock.png
   :alt: The Stock tab of a product

This tab holds the dimensions, the stock amount, and the delivery data of the product. Click ``Save Stock Data`` to
save the changes.

Dimensions & Weight
^^^^^^^^^^^^^^^^^^^

The values relevant for shipping, i.e. of the product in its package: ``Weight``, ``Width``, ``Height`` and
``Length``.

Stock Management
^^^^^^^^^^^^^^^^

Manage stock amount
    If checked, the stock amount decreases when the product is bought, and customers can buy at most the
    ``Stock amount``.

Stock amount
    The amount of the product in stock.

Delivery
^^^^^^^^

Deliverable
    If unchecked, customers see the product but cannot put it into the cart.

Manual delivery time / Delivery time
    By default the delivery time comes from the shipping method that applies to the product. Check ``Manual delivery
    time`` and select a ``Delivery time`` to set it for this product.

Order time
    The time from ordering the product to having it in stock again, when it is out of stock.

Ordered at
    The date when the **shop owner** ordered the product.

.. note::

    If ``Order time`` and ``Ordered at`` are given, the delivery time is calculated from these two fields and the
    delivery time of the product.

Packing
^^^^^^^

Active packing
    If checked, the product is sold only in packings. For variants: ``Standard`` takes the setting of the product,
    ``Yes`` and ``No`` set it for the variant.

Amount per packing
    The amount of products per packing.

Packing unit
    The unit of the packing, displayed after the amount.

.. index:: SEO

.. _products_management_seo:

SEO
---

This tab is used to optimize the product page for search engines. Click ``Save SEO Data`` to save the changes.

Meta title
    Displayed in the title tag of the product page. By default the name of the product.

Meta keywords
    Displayed in the meta keywords tag of the product page.

Meta description
    Displayed in the meta description tag of the product page.

.. note::

    You can use these placeholders in the fields:

    <name>
        The name of the product.

    <short-description>
        The short description of the product (only in meta keywords and meta description).

.. index:: Portlets

.. _products_management_portlets:

Portlets
--------

This tab is used to assign :term:`portlets` to the product.

Blocked parent slots
    By default the product inherits the portlets of its category. To block them, check the slots and click ``Save
    blocked parent slots``.

Slots
    Lists the portlets assigned directly to the product, per slot. Click the pencil to edit a portlet and the trash
    can to delete it. Drag a portlet to change its position or to move it to the other slot.

Add portlet
    Select the ``Portlet Type`` and click ``Add portlet``.

See Also
========

* :ref:`Products in general <products_concepts>`
* :ref:`Portlets in general <portlets_concepts>`
* :ref:`Properties in general <properties_concepts>`
