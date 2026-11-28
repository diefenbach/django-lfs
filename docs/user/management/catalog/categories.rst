.. index:: Category

.. _categories_management:

==========
Categories
==========

This section describes the category management interface (``Catalog / Categories``).

.. image:: /images/manage_category_data.png
   :alt: The Data tab of a category, with the category tree on the left

On the left is the tree of all categories, on the right the selected category with its tabs.

Site Actions
============

Add Top Category
    Adds a category to the root of the catalog.

Add Category
    Adds a sub category to the selected category.

Delete Category
    Deletes the selected category, after a confirmation.

View Category
    Opens the category in the shop.

Category Tree
=============

Search
    Filters the tree by the name of the category.

Expand all / Collapse all
    The buttons beside the heading open or close all branches of the tree.

Move categories
    Click the lock button beside the heading to switch on drag and drop, then drag a category by its handle to its
    new place, also into another category. Click the button again to lock the tree.

Tabs
====

Data
----

Name
    The name of the category. It is displayed in several places, e.g. in category overviews and on top of the
    category page.

Slug
    The unique last part of the category's URL.

Short description
    A short description of the category, used in overviews.

Description
    The detailed description of the category, displayed on the category page.

Exclude from navigation
    If checked, the category is not displayed in the navigation of the shop.

Image
    The image of the category, displayed in category overviews and on the category page.

Static block Above / Static block Below
    An optional :ref:`static block <static_blocks_concepts>`, displayed above resp. below the products or sub
    categories on the category page.

Click ``Save Category Data`` to save the changes.

View
----

.. image:: /images/manage_category_view.png
   :alt: The View tab of a category

Category template
    Decides whether the category page displays the products of the category (``Category with products``) or its sub
    categories (``Category with subcategories``). A theme can provide more templates.

Show all products
    If checked, the category page displays also the products of all sub categories; otherwise only the products
    assigned directly to the category.

Click ``Save View Settings`` to save the changes.

Products
--------

This tab assigns products to the category and removes them.

.. image:: /images/manage_category_products.png
   :alt: The Products tab of a category: all products on the left, the assigned products on the right

Add products
    Select the products in the section ``Products`` and click ``Add to Category``.

Remove products
    Select the products in the section ``Assigned Products`` and click ``Remove from Category``.

Filter
    Above both sections you can search products by name or SKU and filter them by category and manufacturer.

SEO
---

This tab is used to optimize the category page for search engines.

Meta title
    Displayed in the title tag of the category page. The default is ``<name>``, the name of the category.

Meta description
    Displayed in the meta description tag of the category page.

Meta keywords
    Displayed in the meta keywords tag of the category page.

.. note::

    You can use these placeholders in the fields:

    <name>
        The name of the category.

    <short-description>
        The short description of the category (only in meta keywords and meta description).

Click ``Save SEO Settings`` to save the changes.

.. _categories_management_portlets:

Portlets
--------

This tab is used to assign :term:`portlets` to the category.

Blocked parent slots
    By default the category inherits the portlets of its parent category. To block them, check the slots and click
    ``Save blocked parent slots``.

Slots
    Lists the portlets assigned directly to the category, per slot. Click the pencil to edit a portlet and the trash
    can to delete it. Drag a portlet to change its position or to move it to the other slot.

Add portlet
    Select the ``Portlet Type`` and click ``Add portlet``.

See also
========

* :ref:`Categories in general <categories_concepts>`
* :ref:`Portlets in general <portlets_concepts>`
