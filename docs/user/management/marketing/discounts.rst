.. index:: Discount

.. _discounts_management:

=========
Discounts
=========

This section describes the management interface for discounts (``Marketing / Discounts``): price reductions the
cart gets automatically when their criteria are met.

.. image:: /images/manage_discount_data.png
   :alt: The Data tab of a discount

Site Actions
============

Add Discount
    Adds a discount.

Delete Discount
    Deletes the selected discount, after a confirmation.

Tabs
====

Data
----

Name
    The name of the discount, displayed to the customer as an item of the cart and the order.

Active
    Only active discounts are given.

Value
    The value of the discount, an amount or a percentage depending on ``Type``.

Type
    ``Absolute`` (an amount) or ``Percentage`` (of the price of the products in the cart).

Tax
    The tax included in the discount (optional).

SKU
    The id of the discount, e.g. for your accounting.

Sums up
    Whether the discount can be combined with other discounts and vouchers. LFS adds up all discounts and vouchers
    that sum up, takes the highest one that does not, and gives the higher of the two.

Click ``Save discount`` to save the changes.

Criteria
--------

The discount is given only if the cart meets all its criteria, e.g. a minimum cart price or a country. Click
``Add criterion``, select the type, operator and value of each criterion, and click ``Save criteria``.

Products
--------

Without products the discount applies to the whole cart. With products it applies only to them.

Add products
    In the section on the left (searchable by name, filtered by category and manufacturer) select the products and
    click ``Add to Discount``.

Remove products
    In the section ``Assigned Products`` select the products and click ``Remove from Discount``.

See Also
========

* :doc:`/user/concepts/criteria`
