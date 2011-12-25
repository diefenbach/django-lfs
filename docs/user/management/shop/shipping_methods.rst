.. index:: Shipping Method

.. _shipping_methods_management:

================
Shipping methods
================

This section describes the management interface of shipping methods.

Site Actions
============

Add Shipping Method
    Adds a new shipping method.

Delete Shipping Method
    Deletes the currently displayed shipping method

Tabs
====

Data
----

Name
    The name of the shipping method, which is displayed to the shop
    customer (e.g. on the cart and the checkout page).

Description
    A short description of the shipping method, which is displayed to the
    customer (e.g. on the checkout page).

Note
    A note of the shipping method, which is displayed on the confirmation
    mail after the shop customer has been checked out.

Priority
    The first valid shipping method with the highest priority (smaller
    number) method is displayed to the customer as default (if she hasn't
    selected one explicitly).

Image
    An image for the shipping method, which is displayed to the shop
    customer (On the checkout page).

Tax
    The included tax of the shipping method's price.

Price
    The default price of the shipping method. This can be overwritten
    within the price tab (see below).

Delivery time
    The delivery time of the shipping method. See :doc:`delivery_times`.

Criteria
--------

Here you can add criteria for the shipping method. The shipping method is
only available for shop customers if all criteria are true.

Please see :ref:`How to manage shipping methods <how_to_shipping_method_criteria>`
to see how to add criteria.

Prices
------

Here you can add additional prices for the shipping method based on criteria.
If prices are given the first price which meets all criteria is taken for the
shipping method. If no prices are given, the default price of the ``Data`` tab
is taken.

Please see :ref:`How to manage shipping methods <how_to_shipping_method_prices>`
to see how to add prices.

See also
========

* :ref:`General about shipping methods <shipping_methods_concepts>`
* :ref:`How to manage shipping methods <shipping_methods_howto>`
* :ref:`General about criteria <criteria_concepts>`
