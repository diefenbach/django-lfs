===
API
===

Plug-ins
========

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


.. _price_calculator:

PriceCalculator
---------------

.. autoclass:: lfs.plugins.PriceCalculator

    .. automethod:: lfs.plugins.PriceCalculator.get_price

    .. automethod:: lfs.plugins.PriceCalculator.get_price_net

    .. automethod:: lfs.plugins.PriceCalculator.get_price_gross

    .. automethod:: lfs.plugins.PriceCalculator.get_standard_price

    .. automethod:: lfs.plugins.PriceCalculator.get_standard_price_net

    .. automethod:: lfs.plugins.PriceCalculator.get_standard_price_gross

    .. automethod:: lfs.plugins.PriceCalculator.get_for_sale_price

    .. automethod:: lfs.plugins.PriceCalculator.get_for_sale_price_net

    .. automethod:: lfs.plugins.PriceCalculator.get_for_sale_price_gross

    .. automethod:: lfs.plugins.PriceCalculator.get_customer_tax_rate

    .. automethod:: lfs.plugins.PriceCalculator.get_customer_tax

    .. automethod:: lfs.plugins.PriceCalculator.get_product_tax_rate

    .. automethod:: lfs.plugins.PriceCalculator.get_product_tax

    .. automethod:: lfs.plugins.PriceCalculator.price_includes_tax

.. _shipping_method_price_calculator:

ShippingMethodPriceCalculator
-----------------------------

.. autoclass:: lfs.plugins.ShippingMethodPriceCalculator

    .. automethod:: lfs.plugins.ShippingMethodPriceCalculator.get_price_net

    .. automethod:: lfs.plugins.ShippingMethodPriceCalculator.get_price_gross

    .. automethod:: lfs.plugins.ShippingMethodPriceCalculator.get_tax
