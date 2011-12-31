.. index:: Delivery time

.. _delivery_times_concepts:

==============
Delivery Times
==============

This section describes the concepts of delivery times.

Overview
========

LFS calculates automatically the delivery times for single products and the
total cart. Delivery times are managed on a central place and are assigned to
shipping methods, that means they are usually dependent on the first valid or
selected shipping method, if not explicitly overwritten for a product (see
below).

To calculate the delivery time for a single product (to display it within the
product page) LFS takes the first shipping method, which is valid for the
product and customer (all :doc:`criteria </user/concepts/criteria>` are true)
and takes the assigned delivery time of it. It's also possible to override this
mechanism for single products with a :ref:`manually delivery time
<products_management_stock>`.

To calculate the delivery time for the total cart (to display it within the cart
and the checkout page), LFS takes the shipping method the customer has currently
selected and calculates on base of that the maximum delivery time of all
products within the cart. Also in this case the manual delivery times are taken
into account. Is the selected shipping method for a product not valid for this
one the default delivery time is used.

Additionally the :ref:`internal delivery time <products_management_stock>` (shop
owner orders product) can be added to the delivery time for the customer.

See also
========

* :doc:`Delivery Times Management </user/management/shop/delivery_times>`
* :doc:`Shipping Method Management Interface </user/management/shop/shipping_methods>`
* :ref:`Product Management Interface - Stock Data <products_management_stock>`
* :doc:`Criteria concepts </user/concepts/criteria>`
