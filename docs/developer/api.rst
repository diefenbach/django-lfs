===
API
===

This is the public API of LFS.

All changes of it underlies a proper deprecation process and will be announced
explicitly within release notes.

.. _order_payment_method:

PaymentMethod
=============

.. autoclass:: lfs.plugins.PaymentMethod

    .. automethod:: lfs.plugins.PaymentMethod.get_create_order_time

    .. automethod:: lfs.plugins.PaymentMethod.get_pay_link

    .. automethod:: lfs.plugins.PaymentMethod.process

.. _order_number_generator:

OrderNumberGenerator
====================

.. autoclass:: lfs.plugins.OrderNumberGenerator

    .. automethod:: lfs.plugins.OrderNumberGenerator.exclude_form_fields

    .. automethod:: lfs.plugins.OrderNumberGenerator.get_next

    .. automethod:: lfs.plugins.OrderNumberGenerator.get_form
