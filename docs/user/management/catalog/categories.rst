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

In order to sort categories or move it around, hold it on the handle and
drag and drop it to the place you want the category to be.

Tabs
====

Data
----

This tab contains the core date of the category.

Exclude from navigation
    If checked the category is not displayed within the :ref:`categories portlet
    <portlets_concepts_categories>`.

Name
    The name of the category. This is displayed on several places, e.g: within
    category overviews, on top of the category detail view and within the
    meta title tag.

Slug
    The unique last part of the category's URL.

Description
    The detailed description of the category. This is displayed on the detail
    view of the category.

Image
    The image of the category. This can be displayed within category overviews
    and the category detaile view.

.. index:: Static Block

Static block
    An optional :ref:`static block <static_blocks_concepts>` which displayed on
    top of the category detail view.

View
----

This tab contains all data which are responsible on how the content is
displayed.

.. index:: Template

Category template
    The selected template of the category. A category can have several
    templates. The selected templates decides what is displayed (sub templates,
    products) and how this information is structured.

Show all products
    If activated also the products of the sub categories will be displayed
    for that category. Otherwise only the direct products are displayed.

    .. note::

        This is only available when a product template is selected.

.. index:: Formats

Active formats
    If activated you can overwrite the formats. If not activated formats are
    inherited from the parent object. This may be a parent category or the
    shop itself.

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

        This is only available if ``Active formats`` is True and a product
        template is selected.

Products
--------

This tab is used to assign/remove products to the category.

**Filter**

In order to make it easier to find and select several products you can filter
them. This is true for assignable and assigned products. Just put the product
name into the appropriate text box and/or select a certain category.

**Add products**

You can see available products to assign on top of the page. Select the checkboxes
beside all products you want to assign and click on ``Add to category``

**Remove products**

You can see all already assigned products within the ``Selected products`` section.
Select the checkboxes beside the products you want to remove and click on ``Remove
from category``.

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

You can use several placeholders within the above mentioned fields:

    **<name>**

    The name of the product.

    **<short-description>**

    The short description of the product (only within meta
    keywords/description-field).

.. index:: Portlets

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
