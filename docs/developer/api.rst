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
