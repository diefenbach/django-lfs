.. index:: Shipping Method

.. _shipping_methods_management:

================
Shipping methods
================

This section describes the management interface of shipping methods (``Shop / Shipping Methods``).

.. image:: /images/manage_shipping_method_data.png
   :alt: The Data tab of a shipping method

Site Actions
============

Add Shipping Method
    Opens a dialog to add a shipping method with its name.

Delete Shipping Method
    Deletes the selected shipping method, after a confirmation.

Tabs
====

Data
----

Active
    Only active shipping methods are offered to customers.

Name
    The name of the shipping method, displayed to customers, e.g. in the cart and in the checkout.

Description
    A short description, displayed to customers in the checkout.

Note / Image
    A note and an image of the shipping method, for themes that display them; the default theme lfs-theme
    displays neither.

Tax
    The tax included in resp. added to the price.

Price
    The default price of the shipping method. The ``Prices`` tab can replace it (see below).

Delivery time
    The delivery time of the shipping method, see :doc:`delivery_times`.

Price Calculator
    Whether the price includes the tax (``Price includes tax``) or excludes it (``Price excludes tax``).

Click ``Save shipping method`` to save the changes.

Criteria
--------

The shipping method is offered to customers only if all its criteria are met, e.g. a country, a cart price, or a
weight. Click ``Add criterion``, select the type, operator and value of each criterion, and click ``Save
criteria``.

Please see :ref:`How to manage shipping methods <how_to_shipping_method_criteria>` for examples.

Prices
------

Prices that replace the default price when their criteria are met. The first price (lowest ``Priority``) whose
criteria are all met applies; if none applies, the default price of the ``Data`` tab is taken.

* ``Add Price`` adds a price.
* Change ``Priority`` and ``Price`` in the list and click ``Update Prices``; select prices and click ``Delete
  Selected`` to delete them.
* ``Edit Criteria`` opens the criteria of a price.

Please see :ref:`How to manage shipping methods <how_to_shipping_method_prices>` for examples.

See also
========

* :ref:`General about shipping methods <shipping_methods_concepts>`
* :ref:`How to manage shipping methods <shipping_methods_howto>`
* :ref:`General about criteria <criteria_concepts>`
