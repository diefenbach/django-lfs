.. index:: Shipping Method

.. _shipping_methods_concepts:

================
Shipping Methods
================

This section describes the shipping methods of LFS in general.

Overview
========

You can add as many shipping methods as you want. All valid shipping methods are
displayed for selection to the shop customer. A shipping method is valid if all
:doc:`criteria <criteria>` of the shipping method are true. Shipping methods can
have many prices which are also dependent on criteria. The first price which is
valid (all criteria are true) is the current price for the shipping method. If
no price is valid the default price is taken (from the ``Data`` tab).

See Also
========

* :doc:`Manage shipping methods </user/management/shop/shipping_methods>`
