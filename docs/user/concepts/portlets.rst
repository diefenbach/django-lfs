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
object (shop, product, category, page). They are displayed in :term:`slots`. LFS
ships with a left and a right slot and several default portlets. By default
portlets are inherited from parent objects but it is also possible to block
parent portlets per slot.

The inheritance path for categories and products is::

    shop > category > sub category > product

The inheritance path for pages is::

    shop > page root > page

Default Portlets
================

This section describes all default portlets of LFS with there particular
settings and properties.

.. index:: Average Rating Portlet
   single: Portlet; Average Rating

.. _portlets_concepts_average_rating:

Average Rating
--------------

Displays the average rating of a product.

Title
    The title of the portlet.

.. index:: Cart Portlet
   single: Portlet; Cart

.. _portlets_concepts_cart:

Cart
----

Displays the cart of the shop.

Title
    The title of the portlet.

.. index:: Categories Portlet
   single: Portlet; Categories

.. _portlets_concepts_categories:

Categories Portlet
------------------

Displays the category tree of the shop.

Title
    The title of the portlet.

Start Level
    The starting level of categories. If this is, for instance, ``2`` the
    top level categories are not displayed within the portlet.

Expand Level
    Expands the categories up to this level. If this is, for instance, ``1``
    all top level categories are expanded. By default only the categories
    which are selected are expanded.

.. index:: Delivery Time Portlet
   single: Portlet; Delivery Time

.. _portlets_concepts_delivery_time:

Delivery Time
-------------

Displays the delivery time of a product.

Title
    The title of the portlet.

.. index:: Featured Products Portlet
   single: Portlet; Featured Product

.. _portlets_concepts_featured_products:

Featured Products
------------------

Displays featured products

Title
    The title of the portlet.

Limit
    Only the given amount of products are displayed.

Use current category
    If this is checked only the featured product of the current category
    are displayed.

Slideshow
    If this is checked the products are displayed with a slideshow, i.e. a
    single product which is exchanged automatically). If this is unchecked
    all products are display at once.

.. index:: Filter Portlet
   single: Portlet; Filter

.. _portlets_concepts_filter:

Filter
-------

Displays a filter portlet for a category.

Title
    The title of the portlet.

Show Product Filters:
    If this is checked product filters are displayed. To make this work
    properly the products assigned to the category must filterable properties
    and there must be values assigned to them.

Show price filters:
    If this is checked price filters are displayed (which are automatically
    calculated).

.. index:: For Sale Portlet
   single: Portlet; For Sale

.. _portlets_concepts_for_sale:

For Sale
--------

Displays products which are for sale.

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

Displays information pages.

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

Displays related products of a product.

Title
    The title of the portlet.

.. index:: Text Portlet
   single: Portlet; Text

.. _portlets_concepts_text:

Text
----

Displays arbitrary HTML.

Title
    The title of the portlet.

Text
    The HTML code which is supposed to be displayed.


.. index:: Top Seller Portlet
   single: Portlet; Top Seller

.. _portlets_concepts_top_seller:

Top Seller
----------

Displays the top seller of the shop.

Title
    The title of the portlet.

Limit
    Only the given amount of products are displayed.


See Also
========

* :ref:`Shop Preferences <preferences_portlets>`
* :ref:`Categories Management Interface <categories_management_portlets>`
* :ref:`Products Management Interface <products_management_portlets>`
