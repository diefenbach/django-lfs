.. index:: Category

.. _categories_management:

==========
Categories
==========

This section describes the category management interface.

Site Actions
============

Add Top Category
    Adds a category to the root of the catalog.

Add Category
    Adds a sub category to the current displayed category.

Delete Category
    Deletes the current displayed category.

View Category
    Opens the category in a pop-up window to quickly check the appearance of
    the category without leaving the :term:`LMI`.

Goto Category
    Leaves the :term:`LMI` and goes to customer view of the current displayed
    category.

Move Categories
===============

In order to move categories, hold it on the handle left beside the category name
and drag and drop it to the new place.

Tabs
====

Data
----

Exclude from navigation
    If checked the category is not displayed within the :ref:`categories portlet
    <portlets_concepts_categories>`.

Name
    The name of the category. This is displayed on several places, e.g: within
    category overviews and on top of the category detail view.

Slug
    The unique last part of the category's URL.

Description
    The detailed description of the category. This is displayed on the detail
    view of the category.

Image
    The image of the category. This can be displayed within category overviews
    and the category detail view.

Static block
    An optional :ref:`static block <static_blocks_concepts>` which displayed on
    top of the category detail view.

View
----

Category template
    The selected template of the category decides whether the sub categories or
    the products are displayed. It is also possible to provide more templates to
    display single categories individually.

Show all products

    If this check box is activated also the products of the sub categories are
    displayed. Otherwise only the direct products are displayed.

    .. note::

        This is only available when a the products of the category are
        displayed. (see Category Template).

Active formats
    If this check box is activated several formats for this category can be
    overwritten. Otherwise the formats are inherited from the parent object,
    which is either the parent category or the shop.

Category cols
    Amount of columns which are used to display the sub categories. Always all
    direct categories of the category are displayed.

    .. note::

        This is only available if active formats is True and a category
        template is selected.

Product cols / Product rows
    Amount of columns and rows which are used to display the products of the
    category. The amount of products which are displayed calculates by
    cols * rows. If there are more products than that
    the products are automatically paginated.

    .. note::

        This is only available if ``Active Formats`` is True and a product
        template is selected.

Products
--------

This tab is used to assign and remove products to the category.

Add Products
************

In order to assign products to the category, select the check boxes of the
corresponding products within the section ``Selectable Products`` and click on
``Add To Category``.

Remove Products
***************

In order to remove products from the category, select the check boxes beside the
corresponding products  within the section ``Selected Products`` and click on
``Remove From Category``.

Filter
******

In order to make it easier to find products you can filter them by name, SKU and
category. For that enter on top of the according section the name or the SKU
into the text box and select the category out of the select box.

SEO
---

This tab is used to optimize your pages for search engines. You can enter data
for all meta data fields. However LFS provides some reasonable default values
for all fields.

Meta title
    This is displayed within the meta title tag of the category's HTML tags. By
    default the name of the product is used.

Meta keywords
    This is displayed within the meta keywords tag of the category's HTML page.
    By default the short description of the category is used.

Meta description
    This is displayed within the meta description tag of the category's HTML
    page. By default the short description of the category is used.

.. note::

    You can use several placeholders within these fields:

    <name>
        The name of the category.

    <short-description>
        The short description of the category (only within meta keywords and
        meta description field).

.. _categories_management_portlets:

Portlets
--------

This tab is used to assign :term:`portlets` to the category.

Blocked parent slots
    By default portlets are inherited from the parent category. To block
    portlets check the regarding slots and click on the ``Save blocked parent
    slots`` button.

Slots
    Here you can see all directly assigned portlets to the category. In order
    to edit a portlet click on row of the portlet. In order to delete a
    portlet click on the red cross beside the portlet. You can also change
    the position of the portlets by clicking on the up and down arrows beside
    the portlets.

Add new Portlet
    In order to add a portlet to the category select the type of portlet and
    click on ``Add portlet``.

See also
========

* :ref:`Categories in general <categories_concepts>`
* :ref:`Portlets in general <portlets_concepts>`
