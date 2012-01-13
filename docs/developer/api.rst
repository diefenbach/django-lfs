===
API
===

Plugins
=======

.. _order_number_generator:

OrderNumberGenerator
--------------------

.. autoclass:: lfs.plugins.OrderNumberGenerator

    .. automethod:: lfs.plugins.OrderNumberGenerator.exclude_form_fields

    .. automethod:: lfs.plugins.OrderNumberGenerator.get_next

    .. automethod:: lfs.plugins.OrderNumberGenerator.get_form

.. _payment_method:

PaymentMethod
-------------

.. autoclass:: lfs.plugins.PaymentMethod

    .. automethod:: lfs.plugins.PaymentMethod.get_create_order_time

    .. automethod:: lfs.plugins.PaymentMethod.get_pay_link

    .. automethod:: lfs.plugins.PaymentMethod.process


.. _shipping_method_price_calculator:

ShippingMethodPriceCalculator
-----------------------------

.. autoclass:: lfs.plugins.ShippingMethodPriceCalculator

    .. automethod:: lfs.plugins.ShippingMethodPriceCalculator.get_price_net

    .. automethod:: lfs.plugins.ShippingMethodPriceCalculator.get_price_gross

    .. automethod:: lfs.plugins.ShippingMethodPriceCalculator.get_tax
