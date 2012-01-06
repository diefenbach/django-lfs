.. index:: Payment Method

.. _payment_methods_concepts:

===============
Payment Methods
===============

This section describes the concept of payment methods.

Overview
========

You can add as many payment methods as you want.

All valid payment methods are displayed for selection to the shop customer. A
payment method is valid if all :doc:`criteria <criteria>` of the payment method
are true.

Payment methods can have many prices which are, as the payment method itself,
also dependent of criteria. The first price which is valid - all of its criteria
are true - is the current price for the payment method. If no price is valid the
default price is taken (from the ``Data`` tab).

See Also
========

* :doc:`Payment Methods Management Interface </user/management/shop/payment_methods>`
* :doc:`/developer/howtos/how_to_add_own_payment_methods`
* :doc:`Criteria Concepts <criteria>`
