===
API
===

This is the public API of LFS. All changes of this will go through proper
deprecation procesess and will be announced explictly within the release notes.

PaymentMethod
=============

.. autoclass:: lfs.plugins.PaymentMethod

    .. automethod:: lfs.plugins.PaymentMethod.process

    .. automethod:: lfs.plugins.PaymentMethod.get_create_order_time

    .. automethod:: lfs.plugins.PaymentMethod.get_pay_link

OrderNumberGenerator
====================

.. autoclass:: lfs.plugins.OrderNumberGenerator

    .. automethod:: lfs.plugins.OrderNumberGenerator.get_next
