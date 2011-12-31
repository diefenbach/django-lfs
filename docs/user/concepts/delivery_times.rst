.. index:: Delivery time

.. _delivery_times_concepts:

==============
Delivery Times
==============

This section describes the concepts of delivery times.

Overview
========

The delivery time of single products and the cart is calculated automatically by
LFS. Delivery times are managed centrally and are assigned to every existing
shipping method, that means they are usually dependent on the first valid or the
selected shipping method of a customer, if this is not explicitly overwritten
for a product (see below).

To calculate the delivery time for a single product (to display it within the
product page), LFS takes the first valid shipping method for the product and
customer (all :doc:`criteria </user/concepts/criteria>` are true) and takes its
assigned delivery time. It's also possible to override this mechanism for single
products with a :ref:`manually delivery time <products_management_stock>`.

To calculate the delivery time for the total cart (to display it within the cart
and the checkout page), LFS takes the shipping method the customer has currently
selected and calculates on base of that the maximum delivery time of all
products within the cart. Also in this case the manual delivery times of
products are taken into account. Is the currently selected shipping method of a
customer for a product in the cart not valid, the LFS' default delivery time is
used.

Additionally the :ref:`internal delivery time <products_management_stock>` (shop
owner orders product) can be added to the delivery time for the customer.

See also
========

* :doc:`Delivery Times Management </user/management/shop/delivery_times>`
* :doc:`Shipping Method Management Interface </user/management/shop/shipping_methods>`
* :ref:`Product Management Interface - Stock Data <products_management_stock>`
* :doc:`Criteria concepts </user/concepts/criteria>`
