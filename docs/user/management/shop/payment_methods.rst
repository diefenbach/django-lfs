.. index:: Payment Method

.. _payment_methods_management:

================
Payment methods
================

This section describes the management interface of payment methods (``Shop / Payment Methods``).

.. image:: /images/manage_payment_method_data.png
   :alt: The Data tab of a payment method

Site Actions
============

Add Payment Method
    Opens a dialog to add a payment method with its name.

Delete Payment Method
    Deletes the selected payment method, after a confirmation.

Tabs
====

Data
----

Active
    Only active payment methods are offered to customers.

Name
    The name of the payment method, displayed to customers, e.g. in the cart and in the checkout.

Description
    A short description, displayed to customers in the checkout.

Note / Image
    A note and an image of the payment method, for themes that display them; the default theme lfs-theme
    displays neither.

Tax
    The tax included in the price.

Price
    The default price of the payment method. The ``Prices`` tab can replace it (see below).

Module
    The payment processor of an add-on, e.g. ``PayPal`` from lfs-paypal; the list comes from the setting
    ``LFS_PAYMENT_METHOD_PROCESSORS``. Leave it empty for payments without an online provider, like prepayment or
    cash on delivery.

Type
    Which fields the customer fills in in the checkout: ``Plain`` (none), ``Bank`` (bank account) or ``Credit
    Card``.

Click ``Save payment method`` to save the changes.

Criteria
--------

The payment method is offered to customers only if all its criteria are met, e.g. a country, a cart price, or a
weight. Click ``Add criterion``, select the type, operator and value of each criterion, and click ``Save
criteria``.

Please see :ref:`How to manage payment methods <how_to_payment_method_criteria>` for examples.

Prices
------

Prices that replace the default price when their criteria are met. The first price (lowest ``Priority``) whose
criteria are all met applies; if none applies, the default price of the ``Data`` tab is taken.

* ``Add Price`` adds a price.
* Change ``Priority`` and ``Price`` in the list and click ``Update Prices``; select prices and click ``Delete
  Selected`` to delete them.
* ``Edit Criteria`` opens the criteria of a price.

Please see :ref:`How to manage payment methods <how_to_payment_method_prices>` for examples.

See also
========

* :ref:`General about payment methods <payment_methods_concepts>`
* :ref:`How to manage payment methods <payment_methods_howto>`
* :ref:`General about criteria <criteria_concepts>`
