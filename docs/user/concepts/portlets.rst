.. index:: Portlets

.. _portlets_concepts:

========
Portlets
========

This section describes the concept of portlets in general and the default
portlets in detail.

Overview
========

A Portlet is a piece of arbitrary information which can be assigned to every
object, like shop, products, categories and pages. They are displayed in
:term:`slots`. A slot can have an arbitrary amount of Portlets. LFS ships with a
left and a right slot and several default portlets. By default portlets are
inherited from parent objects but it is also possible to block parent portlets
per slot.

The inheritance path for categories and products is::

    shop > category > sub category > product

The inheritance path for pages is::

    shop > page root > page

Default Portlets
================

This section describes all default portlets of LFS with their particular
settings and properties.

.. index:: Average Rating Portlet
   single: Portlet; Average Rating

.. _portlets_concepts_average_rating:

Average Rating
--------------

This portlet displays the average rating of a product.

Title
    The title of the portlet.

.. index:: Cart Portlet
   single: Portlet; Cart

.. _portlets_concepts_cart:

Cart
----

This portlet displays the cart of the shop.

Title
    The title of the portlet.

.. index:: Categories Portlet
   single: Portlet; Categories

.. _portlets_concepts_categories:

Categories Portlet
------------------

This portlet displays the category tree, which is the essential navigation for
the shop.

Title
    The title of the portlet.

Start Level
    The starting level of categories. If this is ``2`` the :term:`top level
    categories` are not displayed within the portlet. This can be useful if you
    want to display them in the horizontal menu.

Expand Level
    Expands the categories up to this level. If this is ``0`` only the current
    category will be expanded. If this is ``1`` all top level categories are
    expanded, etc.

.. note::

    :term:`top level categories` have level 1, their sub categories have Level
    2, etc.


.. index:: Delivery Time Portlet
   single: Portlet; Delivery Time

.. _portlets_concepts_delivery_time:

Delivery Time
-------------

This portlet displays the delivery time of a product.

Title
    The title of the portlet.

.. index:: Featured Products Portlet
   single: Portlet; Featured Product

.. _portlets_concepts_featured_products:

Featured Products
------------------

This portlet displays products, which are selected within :doc:`Marketing /
Featured </user/management/marketing/featured>`

Title
    The title of the portlet.

Limit
    Only the given amount of products are displayed.

Use current category
    If this is checked only the featured product of the current category are
    displayed.

Slideshow
    If this is checked the products are displayed with a slideshow, i.e. a
    single product which is exchanged automatically). If this is unchecked all
    products are display at once.

.. index:: Filter Portlet
   single: Portlet; Filter

.. _portlets_concepts_filter:

Filter
-------

This portlet displays a filter portlet for a category.

Title
    The title of the portlet.

Show Product Filters:
    If this is checked product filters are displayed. To make this work properly
    the products assigned to the category must filterable properties and there
    must be values assigned to them.

Show price filters:
    If this is checked price filters are displayed (which are automatically
    calculated).

.. index:: For Sale Portlet
   single: Portlet; For Sale

.. _portlets_concepts_for_sale:

For Sale
--------

This portlet displays products which are for sale.

Title
    The title of the portlet.

Limit
    Only the given amount of products are displayed.

Use current category
    If this is checked only the featured product of the current category
    are displayed.

Slideshow
    If this is checked the products are displayed via a slideshow, i.e. only
    one product at once which is exchanged automatically. If this is unchecked
    all products are display as a list.

.. index:: Page Portlet
   single: Portlet; Page

.. _portlets_concepts_pages:

Pages
------

This portlet displays information pages.

Title
    The title of the portlet.

.. index:: Recent Portlet
   single: Portlet; Recent

.. _portlets_concepts_recent_products:

Recent Products
---------------

Display the recent visited products.

Title
    The title of the portlet.

.. index:: Related Portlet
   single: Portlet; Related

.. _portlets_concepts_related_products:

Related Products
----------------

This portlet displays related products of a product.

Title
    The title of the portlet.

.. index:: Text Portlet
   single: Portlet; Text

.. _portlets_concepts_text:

Text
----

This portlet displays arbitrary HTML.

Title
    The title of the portlet.

Text
    The HTML code which is supposed to be displayed.


.. index:: Top Seller Portlet
   single: Portlet; Top Seller

.. _portlets_concepts_top_seller:

Top Seller
----------

This portlet displays the top seller of the shop.

Title
    The title of the portlet.

Limit
    Only the given amount of products are displayed.


See Also
========

* :ref:`Shop Preferences <preferences_portlets>`
* :ref:`Categories Management Interface <categories_management_portlets>`
* :ref:`Products Management Interface <products_management_portlets>`
