.. index:: Variants

==================================
How To Add a Product with Variants
==================================

In this how-to you add a linen napkin in three colours: one product with three variants, from which the customer
selects a colour.

Add the product
===============

#. Go to ``Catalog / Products`` and click ``Add Product``.

#. Select the ``Subtype`` ``Product with variants``, enter the ``Name`` ``Linen napkin`` and the ``Slug``
   ``linen-napkin``, and click ``Add Product``.

#. On the ``Data`` tab enter the ``SKU`` (``NP-4040``) and the ``Price`` (``12.90``), select the ``Tax``, check
   ``Active``, and click ``Save Product Data``. Enter the price **before** you add the variants: new variants take
   the price of the product.

Add the colours
===============

#. Go to the ``Variants`` tab.

#. Under ``Local properties`` enter ``Colour`` as ``New property name`` and click ``Add property``.

#. Below ``Colour`` enter ``Sage, Charcoal, Natural`` (comma separated) and click ``Add option``.

.. note::

    Local properties belong only to this product. You can also use the select properties of property groups you
    assigned on the ``Properties`` tab; they appear under ``Add Variants`` as well.

Add the variants
================

#. Under ``Add Variants`` select ``All`` for ``Colour`` and click ``Add variants``. LFS creates one variant per
   colour, with the slugs ``linen-napkin-sage`` and so on, the SKUs ``NP-4040-1`` and so on, and the price of the
   product.

#. In the list of variants check ``Active`` for all variants (new variants are inactive), select the ``Default``
   variant (preselected on the product page), and click ``Save``.

.. image:: /images/howto_variants.png
   :alt: The list of variants of the linen napkin

A variant takes the name, SKU and price of the product until you check the box beside the field in its row and
enter its own value, e.g. a higher price for one colour. The pencil opens the page of a variant with all its
fields; the arrow opens it in the shop.

How the shop shows the variants
===============================

``Display type`` at the bottom of the tab decides how customers choose: ``List`` shows all variants in a list,
``Select`` a select box per property. Select it and click ``Change variant display type``.

``Category variant`` decides which variant category pages show, e.g. the default variant or the cheapest one.

Click ``View Product`` to see the napkin in the shop: the customer selects the colour, and the page shows that
variant.

See also
========

* :ref:`The Variants tab <products_management_variants>`
* :doc:`Products Concept </user/concepts/products>`
* :doc:`Properties Concept </user/concepts/properties>`
