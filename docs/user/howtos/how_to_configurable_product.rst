.. index:: Configurable Product

=================================
How To Add a Configurable Product
=================================

In this how-to you add a linen cushion that customers order in three sizes; the bigger sizes cost more. Unlike a
product with variants, a configurable product is one product: the customer's choice is stored with the cart item
and the order.

Add the property
================

#. Go to ``Properties / Properties`` and click ``Add Property``. Enter the name ``Size``.

#. On the property's page enter the ``Title`` ``Size`` (shown to customers), check ``Configurable``, select the
   ``Type`` ``Select field``, check ``Display price`` and ``Add price``, and click ``Save property``.

#. Under ``Select field options`` add the options with their prices, one after the other: enter the ``Name`` and
   the ``Price`` and click ``Add``:

   * ``40 × 40 cm`` / ``0``
   * ``50 × 50 cm`` / ``4``
   * ``60 × 60 cm`` / ``8``

   With ``Add price`` the price of the selected option is added to the price of the product; with ``Display
   price`` the shop shows it beside the option.

Add the property group
======================

#. Go to ``Properties / Property Groups``, click ``Add Property Group``, and name it ``Cushions``.

#. On the ``Properties`` tab select ``Size`` under ``Available Properties`` and click ``Add to Property Group``.

Add the product
===============

#. Go to ``Catalog / Products`` and click ``Add Product``. Select the ``Subtype`` ``Configurable product``, enter
   the ``Name`` ``Linen cushion`` and the ``Slug``, and click ``Add Product``. The subtype cannot be changed later.

#. On the ``Data`` tab enter the price of the smallest size (``24.90``), select the ``Tax``, check ``Active``, and
   click ``Save Product Data``.

#. On the ``Properties`` tab select the property group ``Cushions`` and click ``Update property groups``.

#. Optionally select the default size under ``Default values`` and click ``Update default values``; it is
   preselected on the product page.

That's it
=========

Click ``View Product``: the product page has a select box ``Size`` with the options and their prices
(``50 × 50 cm / 4.00 EUR``). In the cart the cushion costs its price plus the price of the selected size, e.g.
32.90 for ``60 × 60 cm``.

Properties of the types ``Float field`` and ``Text field`` ask the customer for a number or a text instead.

See Also
========

* :ref:`Product Concepts <products_concepts_configurable_product>`
* :doc:`Property Concepts </user/concepts/properties>`
* :ref:`Properties management <properties_management>`
