.. index:: Delivery time

.. _delivery_times_concepts:

==============
Delivery Times
==============

This section describes the concepts of delivery times.

Overview
========

Delivery times are used to calculate the delivery time for single products or
the total cart.

The common way how to use delivery times is to assign them to :doc:`shipping
methods </user/management/shop/shipping_methods>`. The delivery time of a
product and the total cart is then calculated by LFS automatically.

To calculate the delivery time for a single product LFS takes the first valid
shipping method for the current customer, i.e. the first shipping method which
meets all :doc:`criteria </user/concepts/criteria>`.

To calculate the delivery time for the total cart LFS takes the shipping method
the customer has currently selected. In this way the customer can see in real
time how long a delivery would take when he changes the shipping method from
standard to express for instance.

It is also possible to overwrite this mechanism for single products with a
:ref:`manually delivery time <products_management_stock>`.

See Also
========

* :doc:`Delivery Times Management </user/management/shop/delivery_times>`
* :doc:`Shipping Method Management Interface </user/management/shop/shipping_methods>`
* :ref:`Product Management Interface - Stock Data <products_management_stock>`
* :doc:`Criteria concepts </user/concepts/criteria>`
