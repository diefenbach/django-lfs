.. index:: Filter

==========================
How To Add Product Filters
==========================

In this how-to you let customers filter the kitchen textiles by colour. At the end the category page shows a
filter with the price range and the colours, each with the number of products.

.. image:: /images/howto_filters_shop.png
   :alt: A category page with the filter: price range and colours

Add the filter portlet
======================

The filter is a :term:`portlet`. Assigned to the shop, it appears on all categories.

#. Go to ``Shop / Preferences``, tab ``Portlets``.

#. Select the ``Portlet Type`` ``Filter`` and click ``Add portlet``.

#. In the dialog select the slot ``Left``, keep ``Show product filters`` and ``Show price filters`` checked, and
   click ``Save portlet``.

Add the property
================

#. Go to ``Properties / Properties``, click ``Add Property``, and name it ``Colour``.

#. Enter the ``Title`` ``Colour``, check ``Filterable``, select the ``Type`` ``Select field``, and click ``Save
   property``.

#. Under ``Select field options`` add ``Sage``, ``Charcoal`` and ``Natural``: enter the ``Name`` and click ``Add``.

Add the property group
======================

#. Go to ``Properties / Property Groups``, click ``Add Property Group``, and name it ``Textiles``.

#. On the ``Properties`` tab select ``Colour`` under ``Available Properties`` and click ``Add to Property Group``.

#. On the ``Products`` tab select the textiles under ``Available Products`` and click ``Add to Property Group``.

Give the products their colour
==============================

For every product:

#. Go to its ``Properties`` tab.

#. Under ``Filter values`` select its colour and click ``Update filter values``. Set the same colour under
   ``Displayed values`` (``Update displayed values``) to show it on the product page as well.

That's it
=========

The category ``Kitchen textiles`` now shows the filter. A customer who checks ``Sage`` sees only the sage apron; the
numbers in brackets count the products per colour.

See also
========

* :doc:`Properties Concept </user/concepts/properties>`
* :ref:`The Properties tab of a product <products_management_properties>`
