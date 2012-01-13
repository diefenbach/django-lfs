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

.. _payment_method_proccessor:

PaymentMethodProcessor
----------------------

.. autoclass:: lfs.plugins.PaymentMethodProcessor

    .. automethod:: lfs.plugins.PaymentMethodProcessor.get_create_order_time

    .. automethod:: lfs.plugins.PaymentMethodProcessor.get_pay_link

    .. automethod:: lfs.plugins.PaymentMethodProcessor.process


.. _shipping_method_price_calculator:

ShippingMethodPriceCalculator
-----------------------------

.. autoclass:: lfs.plugins.ShippingMethodPriceCalculator

    .. automethod:: lfs.plugins.ShippingMethodPriceCalculator.get_price_net

    .. automethod:: lfs.plugins.ShippingMethodPriceCalculator.get_price_gross

    .. automethod:: lfs.plugins.ShippingMethodPriceCalculator.get_tax
