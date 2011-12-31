.. index:: Criteria

.. _criteria_concepts:

========
Criteria
========

This section describes the concepts of criteria.

Overview
========

Criteria are a central concept of LFS and are used on several places in order
to restrict or display information on base of the current situation. For
example: which products are in the cart or in which country are these products
about to be delivered. Criteria have a value and an operator, which are the base
whether the criteria is true or false. This is described in more detail in the
section ``Criteria`` below.

Criteria are used within:

* Payment methods

* Payment method's prices

* Shipping methods

* Shipping method's prices

* Discounts

For example a shipping method is only available when all of its criteria are
true.

Criteria
========

This paragraph describes the existing types of criteria and which operators they
provide.

Cart Price
-----------

Description
^^^^^^^^^^^

Tests the gross price of all products within the cart (without costs for
shipping, payment and so on).

Value
^^^^^

A number against the gross price of all products within the cart is tested.

Operators
^^^^^^^^^

Equal
    The criterion is true, if the gross price of the cart is equal to the
    entered value.

Less than
    The criterion is true, if the gross cart price is less than the entered
    value.

Less than equal to
    The criterion is true, if the gross cart price is less than or equal to
    the entered value.

Greater than
    The criterion is true, if the gross cart price is greater than the entered
    value.

Greater than equal to
    The criterion is true, if the gross cart price is greater than or equal to
    the entered value.

Payment Method
--------------

Description
^^^^^^^^^^^

Provides some tests for the payment methods of the shop.

Value
^^^^^

Any selection out of all provided payment methods.

Operators
^^^^^^^^^

Is selected
    The criterion is true if the current selected payment method is within
    the selected payment methods.

Is not selected
    The criterion is true if the current selected payment method is not within
    the selected payment methods.

Is valid
    The criterion is true if all of the selected payment methods are valid.

Is not valid
    The criterion is true if all of the selected payment methods are not
    valid.

Shipping Method
---------------

Description
^^^^^^^^^^^

Provides some tests for the shipping methods of the shop.

Value
^^^^^

Any selection out of all provided shipping methods.

Operators
^^^^^^^^^

Is selected
    The criterion is true if the current selected shipping method is within
    the selected shipping methods.

Is not selected
    The criterion is true if the current selected shipping method is not within
    the selected shipping methods.

Is valid
    The criterion is true if all of the selected shipping methods are valid.

Is not valid
    The criterion is true if all of the selected shipping methods are not
    valid.

Country
-------

Description
^^^^^^^^^^^

Tests the country of the customer's shipping address.

Value
^^^^^

An arbitrary selection out of all existing countries.

Operators
^^^^^^^^^

Is
    The criterion is true, if the customer's shipping country is within the
    selection of countries.

Is not
    The criterion is true, if the customer's shipping country is not within the
    selection of countries.

Combined Length And Girth
-------------------------

Description
^^^^^^^^^^^

Tests the total combined length and girth (clag) of all products within the
cart. The clag is calculated as following::

    (2 * maximum width) + (2 * total height) + maximal length

Value
^^^^^

A number against the total combined length and girth of all products within the
cart is tested.

Operators
^^^^^^^^^

Equal
    The criterion is true, if the total clag is equal to the entered value.

Less than
    The criterion is true, if the total clag is less than the entered value.

Less than equal to
    The criterion is true, if the total clag is less than equal to the entered
    value.

Greater than
    The criterion is true, if the total clag is greater than the entered value.

Greater than equal to
    The criterion is true, if the total clag is greater than equal to the
    entered value.

Height
------

Description
^^^^^^^^^^^

Tests the total height of all products within the cart.

Value
^^^^^

A number against the total height of all products within the cart is tested.

Operators
^^^^^^^^^

Equal
    The criterion is true, if the total height of all products within the cart
    is equal to the entered value.

Less than
    The criterion is true, if the total height of all products within the cart
    is less than the entered value.

Less than equal to
    The criterion is true, if the total height of all products within the cart
    is less than equal to the entered value.

Greater than
    The criterion is true, if the total height of all products within the cart
    is greater than the entered value.

Greater than equal to
    The criterion is true, if the total height of all products within the cart
    is greater than equal to the entered value.

Length
------

Description
^^^^^^^^^^^

Tests the maximum length of all products within the cart.

Value
^^^^^

A number against the maximum length of all products within the cart is tested.

Operators
^^^^^^^^^

Equal
    The criterion is true, if the maximum length of all products within the cart
    is equal to the entered value.

Less than
    The criterion is true, if the maximum length of all products within the cart
    is less than the entered value.

Less than equal to
    The criterion is true, if the maximum length of all products within the cart
    is less than equal to the entered value.

Greater than
    The criterion is true, if the maximum length of all products within the cart
    is greater than the entered value.

Greater than equal to
    The criterion is true, if the maximum length of all products within the cart
    is greater than equal to the entered value.

Weight
------

Description
^^^^^^^^^^^

Tests the total weight of all products within the cart.

Value
^^^^^

A number against the total weight of all products within the cart is tested.

Operators
^^^^^^^^^

Equal
    The criterion is true, if the total weight of all products within the cart
    is equal to the entered value.

Less than
    The criterion is true, if the total weight of all products within the cart
    is less than the entered value.

Less than equal to
    The criterion is true, if the total weight of all products within the cart
    is less than equal to the entered value.

Greater than
    The criterion is true, if the total weight of all products within the cart
    is greater than the entered value.

Greater than equal to
    The criterion is true, if the total weight of all products within the cart
    is greater than equal to the entered value.

Width
-----

Description
^^^^^^^^^^^

Tests the maximum width of all products within the cart.

Value
^^^^^

A number against the maximum width of all products within the cart is tested.

Operators
^^^^^^^^^

Equal
    The criterion is true, if the maximum width of all products within the cart
    is equal to the entered value.

Less than
    The criterion is true, if the maximum width of all products within the cart
    is less than the entered value.

Less than equal to
    The criterion is true, if the maximum width of all products within the cart
    is less than equal to the entered value.

Greater than
    The criterion is true, if the maximum width of all products within the cart
    is greater than the entered value.

Greater than equal to
    The criterion is true, if the maximum width of all products within the cart
    is greater than equal to the entered value.
