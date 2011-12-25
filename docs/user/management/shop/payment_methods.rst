.. index:: Payment method

.. _payment_methods_management:

===============
Payment methods
===============

This section describes the management interface of payment methods.

Overview
========

* You can add as many payment methods as you want.

* All valid payment methods are displayed for selection to the shop customer.

* A payment method is valid if all criteria of the payment method are true.

* Payment methods can have many prices which are dependent of criteria. The
  first price which is valid (all criteria are true) is the current price for
  the the payment method. If no price is valid the default price is taken
  (from data tab).

Data
====

Name
    The name of the payment method, which is displayed to the shop
    customer (e.g. on the cart and the checkout page).

Description
    A short description of the payment method, which is displayed to the
    customer (e.g. on the checkout page).

Note
    A note of the payment method, which is displayed on the confirmation
    mail after the shop customer has been checked out.

Priority
   The first valid payment method with the highest priority (smaller
   number) method is displayed to the customer as default (if she hasn't
   selected one explicitly).

Image
    An image for the payment method, which is displayed to the shop
    customer.

Tax
    The included tax of the payment method's price

Price
    The default price of the payment method. This can be overwritten
    within the price tab (see below).

Module
    The dotted name of the external package which processes the payment
    (this is for developers only).

Type
    The type of the payment method. Dependent on that additional fields
    for input (within the checkout process) will be displayed. There are
    three types at the moment:

      * Plain
        No additional fields are displayed.

      * Bank
        Fields for a bank account are displayed.

      * Credit Card
        Fields for a credit card are displayed.

Criteria
========

Here you can add criteria for the payment method. The payment method is
only available for shop customers if all criteria are true.

Please see :ref:`How to manage payment methods <how_to_payment_method_criteria>`
to see how to add criteria.

Prices
======

Here you can add additional prices for the payment method based on criteria.
If prices are given the first price which meets all criteria is taken for the
payment method. If no prices are given, the default price of the ``Data`` tab
is taken.

Please see :ref:`How to manage payment methods <how_to_payment_method_prices>`
to see how to add prices.

See also
========

* :ref:`How to manage payment methods <payment_methods_howto>`
* :ref:`General about criteria <criteria_concepts>`
