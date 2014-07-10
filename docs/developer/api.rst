===
API
===

Plug-ins
========

.. _api_criterion:

Criterion
---------

.. py:class:: lfs.criteria.models.Criterion

    Base class for all criteria.

    **Attributes:**

    cart
        The current cart of the current customer.

    content
        The content object the criterion belongs to.

    operator
        The current selected operator for the criterion.

    position
        The position of the criterion within a list of criteria of the
        content object.

    product
        The product, if the criterion is called from a product detail view.
        Otherwise this is None.

    request
        The current request.

    **Constants:**

    EQUAL, LESS_THAN, LESS_THAN_EQUAL, GREATER_THAN, GREATER_THAN_EQUAL, IS_SELECTED, IS_NOT_SELECTED, IS_VALID, IS_NOT_VALID, CONTAINS
        Integers which represents certain operators.

    INPUT, SELECT, MULTIPLE_SELECT
        Constants which represents the types of selectable values. One of
        these must be returned from ``get_value_type``.

    NUMBER_OPERATORS
        A list of operators which can be returned from ``get_operators``.

        .. code-block:: python

            [
                [EQUAL, _(u"Equal to")],
                [LESS_THAN, _(u"Less than")],
                [LESS_THAN_EQUAL, _(u"Less than equal to")],
                [GREATER_THAN, _(u"Greater than")],
                [GREATER_THAN_EQUAL, _(u"Greater than equal to")],
            ]


    SELECTION_OPERATORS
        A list of operators which can be returned from ``get_operators``.

        .. code-block:: python

            [
                [IS_SELECTED, _(u"Is selected")],
                [IS_NOT_SELECTED, _(u"Is not selected")],
            ]

    VALID_OPERATORS
        A list of operators which can be returned from ``get_operators``.

        .. code-block:: python

            [
                [IS_VALID, _(u"Is valid")],
                [IS_NOT_VALID, _(u"Is not valid")],
            ]

    STRING_OPERATORS
        A list of operators which can be return from ``get_operators``.

        .. code-block:: python

            [
                [EQUAL, _(u"Equal to")],
                [CONTAINS, _(u"Contains")],
            ]

    .. py:method:: lfs.criteria.models.Criterion.get_operators

        Returns the selectable operators of the criterion which are displayed to
        the shop manager. This is a list of list, whereas the the first value is
        integer, which is stored within the criterion and the second value is
        the string which is displayed to the shop manager, e.g.:

        .. code-block:: python

            [
                [0, _(u"Equal to")],
                [1, _(u"Less than")],
                [2, _(u"Less than equal to")],
                [3, _(u"Greater than")],
                [4, _(u"Greater than equal to")],
            ]

        .. note::

            You can use one of the provided class attributes, see above.

            * NUMBER_OPERATORS
            * SELECTION_OPERATORS
            * VALID_OPERATORS
            * STRING_OPERATORS

    .. py:method:: lfs.criteria.models.Criterion.get_selectable_values(request)

        Returns the selectable values as a list of dictionary, see below. This
        is only called when ``get_value_type`` returns SELECT or
        MULTIPLE_SELECT.

        .. code-block:: python

            [
                {
                    "id": 0,
                    "name": "Name 0",
                    "selected": False,
                },
                {
                    "id": 1,
                    "name": "Name 1",
                    "selected": True,
                },
            ]

    .. py:method:: lfs.criteria.models.Criterion.get_template(request)

        Returns the template to render the criterion.

    .. py:method:: lfs.criteria.models.Criterion.get_value_type

        Returns the type of the selectable values field. Must return one of:

        * self.INPUT
        * self.SELECT
        * self.MULTIPLE_SELECT

    .. py:method:: lfs.criteria.models.Criterion.get_value

        Returns the current value of the criterion.

    .. py:method:: lfs.criteria.models.Criterion.is_valid(request, product=None)

        Returns ``True`` if the criterion is valid otherwise ``False``.

    .. py:method:: lfs.criteria.models.Criterion.render(request, position)

        Renders the criterion as html in order to displayed it within the
        management form.

    .. py:method:: lfs.criteria.models.Criterion.update(value)

        Updates the value of the criterion.

        **Parameters:**

        value
            The value the shop user has entered for the criterion.

.. _order_number_generator:

OrderNumberGenerator
--------------------

.. py:class::  lfs.plugins.OrderNumberGenerator

    Base class from which all order number generators should inherit.

    **Attributes:**

    cart

        The current cart of the customer.

    customer

        The customer of the order.

    order

        The order for which a new number is generated.

    request

        The current request

    user

        The user of the order.

    .. py:method:: lfs.plugins.OrderNumberGenerator.get_form(**kwargs)

        Returns the form which is used within the shop preferences management
        interface.

        All parameters are passed to the form.

    .. py:method:: lfs.plugins.OrderNumberGenerator.get_next(formatted=True)

        Returns the next order number as string. Derived classes must implement
        this method.

        **Parameters:**

        formatted
            If True the number will be returned within the stored format, which
            is based on Python default string formatting operators, e.g.
            ``%04d``.

    .. py:method:: lfs.plugins.OrderNumberGenerator.exclude_form_fields

        Returns a list of fields, which are excluded from the model form, see
        also ``get_form``.

    .. py:method:: lfs.plugins.OrderNumberGenerator.init(request, order)

        Initializes the order number generator. This method is called
        automatically from LFS.

.. _payment_method_proccessor:

PaymentMethodProcessor
----------------------

.. py:class:: lfs.plugins.PaymentMethodProcessor(request, cart=None, order=None)

    Base class from which all 3rd-party payment method processors should inherit.

    **Attributes:**

    cart
        The current cart. This is only set, when create order time is ACCEPTED.

    order
        The current order. This is only set, when create order time is
        IMMEDIATELY.

    request
        The current request.

    .. py:method:: lfs.plugins.PaymentMethodProcessor.get_create_order_time

        Returns the time when the order should be created. It is one of:

        PM_ORDER_IMMEDIATELY
            The order is created immediately before the payment is processed.

        PM_ORDER_ACCEPTED
            The order is created when the payment has been processed and
            accepted.

    .. py:method:: lfs.plugins.PaymentMethodProcessor.get_pay_link

        Returns a link to the payment service to pay the current order, which
        is displayed on the thank-you page and the order confirmation mail. In
        this way the customer can pay the order again if something has gone
        wrong.

    .. py:method:: lfs.plugins.PaymentMethodProcessor.process

        Implements the processing of the payment method. Returns a dictionary
        with several status codes, see below.

        **Return Values:**

        This values are returned within a dictionary.

        accepted (mandatory)
            Indicates whether the payment is accepted or not. if this is
            ``False`` the customer keeps on the checkout page and gets
            ``message`` (if given) below. If this is ``True`` the customer will
            be redirected to next_url (if given).

        message (optional)
            This message is displayed on the checkout page, when the order is
            not accepted.

        message_location (optional)
            The location, where the message is displayed.

        next_url (optional)
            The url to which the user is redirect after the payment has been
            processed. if this is not given the customer is redirected to the
            default thank-you page.

        order_state (optional)
            The state in which the order should be set. It's just PAID. If it's
            not given the state keeps in SUBMITTED.

.. _price_calculator:

PriceCalculator
---------------

.. py:class:: lfs.plugins.PriceCalculator(request, product, **kwargs)

    This is the base class that pricing calculators must inherit from.

    **Attributes:**

    product
        The product for which the price is calculated.

    request
        The current request.

    .. py:method:: lfs.plugins.PriceCalculator.get_base_price(with_properties=True)

        Returns the base price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_base_price_net(with_properties=True)

        Returns the net base price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_base_price_gross(with_properties=True)

        Returns the gross base price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_base_packing_price(with_properties=True)

        Returns the base packing price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_base_packing_price_net(with_properties=True)

        Returns the base packing net price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_base_packing_price_gross(with_properties=True)

        Returns the base packing gross price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_customer_tax(with_properties=True)

        Returns the calculated tax for the current customer and product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the taxes of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_customer_tax_rate

        Returns the tax rate for the current customer and product.

    .. py:method:: lfs.plugins.PriceCalculator.get_effective_price

        Effective price is used for sorting and filtering. Usually it is same as
        value from get_price but in some cases it might differ (eg. if we add
        eco tax to product price)

    .. py:method:: lfs.plugins.PriceCalculator.get_for_sale_price(with_properties=True)

        Returns the sale price for the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_for_sale_price_net(with_properties=True)

        Returns the sale net price for the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_for_sale_price_gross(with_properties=True)

        Returns the sale net price for the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_price(with_properties=True)

        Returns the stored price of the product without any tax calculations.
        It takes variants, properties and sale prices into account, though.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_price_net(with_properties=True)

        Returns the net price of the product.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_price_gross(with_properties=True)

        Returns the real gross price of the product. This is the base of
        all price and tax calculations.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_standard_price(with_properties=True)

        Returns always the stored standard price for the product. Independent
        whether the product is for sale or not. If you want the real price of
        the product use ``get_price`` instead.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_standard_price_net(with_properties=True)

        Returns always the standard net price for the product. Independent
        whether the product is for sale or not. If you want the real net price
        of the product use ``get_price_net`` instead.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_standard_price_gross(with_properties=True)

        Returns always the gross standard price for the product. Independent
        whether the product is for sale or not. If you want the real gross
        price of the product use ``get_price_gross`` instead.

        **Parameters:**

        with_properties
            If the instance is a configurable product and with_properties is
            True the prices of the default properties are added to the price.

    .. py:method:: lfs.plugins.PriceCalculator.get_product_tax(with_properties=True)

        Returns the calculated tax for the current product independent of the
        customer.

    .. py:method:: lfs.plugins.PriceCalculator.get_product_tax_rate

        Returns the stored tax rate of the product. If the product is a variant
        it returns the parent's tax rate.

    .. py:method:: lfs.plugins.PriceCalculator.price_includes_tax

        Returns True if stored price includes tax. False if not.

.. _shipping_method_price_calculator:

ShippingMethodPriceCalculator
-----------------------------

.. py:class:: lfs.plugins.ShippingMethodPriceCalculator(request, shipping_method)

    Base class from which all 3rd-party shipping method prices should inherit.

    **Attributes:**

    request
        The current request.

    shipping_method
        The shipping method for which the price is calculated.

    .. py:method:: lfs.plugins.ShippingMethodPriceCalculator.get_price

        Returns the stored price without any calculations.

    .. py:method:: lfs.plugins.ShippingMethodPriceCalculator.get_price_gross

        Returns the gross price of the shipping method.

    .. py:method:: lfs.plugins.ShippingMethodPriceCalculator.get_price_net

        Returns the net price of the shipping method.

    .. py:method:: lfs.plugins.ShippingMethodPriceCalculator.get_tax

        Returns the total tax of the shipping method.

    .. py:method:: lfs.plugins.ShippingMethodPriceCalculator.get_tax_rate

        Returns the tax rate of the shipping method.
