.. index:: Shipping Method

.. _shipping_methods_howto:

==============================
How To Manage Shipping Methods
==============================

In this how-to you add a shipping method, restrict it with criteria, and give it a second price: parcels up to
30 kg cost 4.90, and from a cart price of 50 shipping is free.

Add the shipping method
=======================

#. Go to ``Shop / Shipping Methods`` and click ``Add Shipping Method``.

#. Enter the ``Name``, e.g. ``Parcel``, and click ``Add Shipping Method`` in the dialog. The ``Data`` tab of the new
   shipping method opens.

#. Check ``Active``, enter a ``Description`` for the checkout, select the ``Tax`` and the ``Delivery time``, enter
   the ``Price`` (``4.90``), and select the ``Price Calculator`` (whether the price includes the tax).

#. Click ``Save shipping method``.

.. _how_to_shipping_method_criteria:

Restrict it with criteria
=========================

The shipping method is offered only if all its criteria are met. Here: the weight of all cart items is at most
30.

.. image:: /images/howto_shipping_criteria.png
   :alt: The Criteria tab of a shipping method with a weight criterion

#. Go to the ``Criteria`` tab and click ``Add criterion``. A new row appears.

#. Select the ``Type`` ``Weight``, the ``Operator`` ``Less than equal to``, and enter the ``Value`` ``30``.

#. Click ``Save criteria``.

The plus button of a row adds another criterion below it, the trash can removes the row; both take effect with
``Save criteria``. The types offered are those of the setting ``LFS_CRITERIA``: cart price, combined length and
girth, country, height, length, width, weight, shipping method and payment method.

.. _how_to_shipping_method_prices:

Add a second price
==================

A shipping method can have more prices, each with its own criteria. The first price (lowest ``Priority``) whose
criteria are all met replaces the price of the ``Data`` tab. Here: shipping is free from a cart price of 50.

.. image:: /images/howto_shipping_prices.png
   :alt: The Prices tab of a shipping method with a free shipping price

#. Go to the ``Prices`` tab and click ``Add Price``. A new row appears.

#. Enter the ``Price`` ``0`` and the ``Priority`` ``10`` and click ``Update Prices``.

#. Click ``Edit Criteria`` beside the price. A dialog opens.

   .. image:: /images/howto_shipping_price_criteria.png
      :alt: The dialog with the criteria of a price

#. Click ``Add criterion``, select the ``Type`` ``Cart Price``, the ``Operator`` ``Greater than equal to``, enter
   the ``Value`` ``50``, and click ``Save Criteria``.

The Prices tab now shows the criteria beside the price. A cart of 19.50 pays 4.90 for shipping, a cart of 79.00
nothing.

To delete prices, select them and click ``Delete Selected``.

See Also
========

* :ref:`Manage shipping methods <shipping_methods_management>`
* :ref:`Criteria in general <criteria_concepts>`
