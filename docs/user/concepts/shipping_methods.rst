.. index:: Shipping Methods

.. _shipping_methods_concepts:

================
Shipping Methods
================

This section describes the concept of shipping methods.

Overview
========

You can add as many :doc:`shipping methods </user/howtos/how_to_shipping_method>`
as you want.

All *valid* shipping methods are displayed for selection to the shop customer. A
shipping method is valid if all :doc:`criteria <criteria>` of the shipping
method are true.

Shipping methods can have many prices which are, as the payment method itself,
also dependent on criteria. The first price which is valid - all of its criteria
are true - is the current price for the shipping method. If no price is valid
the default price is taken (from the ``Data`` tab).

Shipping methods have also a :doc:`delivery time
</user/concepts/delivery_times>` which decides how long the delivery will take
if a certain shipping method is selected by the customer.

See also
========

* :doc:`Shipping Method Management Interface </user/management/shop/shipping_methods>`
* :doc:`Delivery Time Concepts </user/concepts/delivery_times>`
* :doc:`Criteria Concepts <criteria>`
