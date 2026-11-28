.. index:: Payment method

.. _payment_methods_howto:

=============================
How To Manage Payment Methods
=============================

In this how-to you set up cash on delivery: only for customers in Germany, and with a fee of 3.50.

Edit the payment method
=======================

``lfs_init`` has already created ``Cash on delivery``; other payment methods you add with ``Add Payment Method``
in the same way.

#. Go to ``Shop / Payment Methods`` and select ``Cash on delivery``.

#. On the ``Data`` tab check ``Active``, enter a ``Description`` for the checkout, the ``Price`` ``3.50`` (the
   fee), and select its ``Tax``. Leave ``Module`` empty: no online provider processes the payment. ``Type`` stays
   ``Plain``, so the checkout asks for no bank account or card.

#. Click ``Save payment method``.

.. _how_to_payment_method_criteria:

Restrict it with criteria
=========================

The payment method is offered only if all its criteria are met. Here: the customer's country is Germany.

.. image:: /images/howto_payment_criteria.png
   :alt: The Criteria tab of a payment method with a country criterion

#. Go to the ``Criteria`` tab and click ``Add criterion``. A new row appears.

#. Select the ``Type`` ``Country`` and the ``Operator`` ``Is selected``, and select ``Germany`` in the list of
   values. The list offers the shipping countries of the shop.

#. Click ``Save criteria``.

The plus button of a row adds another criterion below it, the trash can removes the row; both take effect with
``Save criteria``.

.. _how_to_payment_method_prices:

Prices depending on criteria
============================

Like shipping methods, payment methods can have more prices, each with its own criteria, e.g. no fee from a cart
price of 100. The ``Prices`` tab works exactly like the one of shipping methods: see :ref:`the shipping how-to
<how_to_shipping_method_prices>`.

See Also
========

* :ref:`Manage payment methods <payment_methods_management>`
* :doc:`how_to_paypal`
* :ref:`Criteria in general <criteria_concepts>`
