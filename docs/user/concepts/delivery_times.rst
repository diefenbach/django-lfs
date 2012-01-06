.. index:: Delivery time

.. _delivery_times_concepts:

==============
Delivery Times
==============

This section describes the concepts of delivery times.

Overview
========

The delivery times of single products and the cart is calculated automatically
by LFS. Delivery times are :doc:`managed centrally
</user/management/shop/delivery_times>` and :doc:`are assigned to LFS' shipping
methods </user/management/shop/shipping_methods>`, that means they are generally
dependent on the first valid or the selected shipping method of a customer, if
this is not explicitly overwritten for a product (see below).

Products
========

To get the delivery time for a single product (to display it within the product
page), LFS calculates the first valid shipping method for the product and the
customer (all :doc:`criteria </user/concepts/criteria>` are true) and takes its
assigned delivery time. It's also possible to override this mechanism for single
products with a :ref:`manually delivery time <products_management_stock>`.

Cart
====

To identify the delivery time for the total cart (to display it within the cart
and the checkout page), LFS takes the shipping method the customer has currently
selected and calculates on base of that the maximum delivery time of all
products within the cart. The result can different from the selected shipping
method as also in this case the manual delivery times of products are taken into
account. Additionally the default delivery time is used if the selected shipping
method for are product within the cart is not valid.

Miscellaneous
=============

Additionally the :ref:`internal delivery time <products_management_stock>` (shop
owner orders product) can be added to the delivery time for the customer.

See also
========

* :doc:`Delivery Times Management </user/management/shop/delivery_times>`
* :doc:`Shipping Method Management Interface </user/management/shop/shipping_methods>`
* :ref:`Product Management Interface - Stock Data <products_management_stock>`
* :doc:`Criteria concepts </user/concepts/criteria>`
