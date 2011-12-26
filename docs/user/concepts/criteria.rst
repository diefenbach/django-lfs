.. index:: Criteria

.. _criteria_concepts:

========
Criteria
========

This section describes the concepts of criteria.

Overview
========

Criteria are a central concept and used on several locations of LFS in order to
restrict respectively display information dependent on different contexts.

At the moment criteria are used within:

* Payment methods

* Payment method's prices

* Shipping methods

* Shipping method's prices

* Discounts

In future they might be used to provide:

* Multiple product prices

* Different product taxes

Types
=====

This paragraph describes which types of criteria exists and which operators
they provide.

Cart Price
-----------

Description
^^^^^^^^^^^

Provides some tests against the the total gross price of all products of the
cart (without other costs like shipping, payment and so on).

Value
^^^^^

A number which describes a price level. How this is interpreted is up
to the used operator (see below).

Operators
^^^^^^^^^

Equal
    The cart price is equal to the entered value

Less than
    The criterion is true if the cart price is less than the entered value.

Less than equal to
    The criterion is true if the cart price is less than equal to the entered
    value.

Greater than
    The criterion is true if the cart price is greater than the entered value.

Greater than equal to
    The criterion is true if the cart price is greater than equal to the
    entered value

Combined Length And Girth
-------------------------

Description
^^^^^^^^^^^

Provides some tests against the total combined length and girth (clag) of all
products within the cart. The "clag" is calculated as following::

    (2 * maximum width) + (2 * total height) + maximal length

Value
^^^^^

A number which describes a clag level. How this is interpreted is up to the
used operator (see below).

Operators
^^^^^^^^^

Equal
    The criterion is true if the clag is equal to the entered value.

Less than
    The criterion is true if the clag is less than the entered value.

Less than equal to
    The criterion is true if the clag is less than equal to the entered value.

Greater than
    The criterion is true if the clag is greater than the entered value.

Greater than equal to
    The criterion is true if the clag is greater than equal to the entered
    value.

Country
-------

Description
^^^^^^^^^^^

Provides some tests against the the country of the current customer's shipping
address.

Value
^^^^^

An arbitrary selection out of all provided countries.

Operators
^^^^^^^^^

Is
    The criterion is true if the shipping country of the customer is within
    the selected countries.

Is not
    The criterion is true if the shipping country of the customer is not within
    selected countries.

Height
------

Description
^^^^^^^^^^^

Provides some tests against the total height of all products within the cart.

Value
^^^^^

A number which describes a height level. How this is interpreted is up
to the used operator (see below).

Operators
^^^^^^^^^

Equal
    The total height is equal to the entered value

Less than
    The criterion is true if the total height is less than the entered value.

Less than equal to
    The criterion is true if the total height is less than equal to the entered
    value.

Greater than
    The criterion is true if the total height is greater than the entered
    value.

Greater than equal to
    The criterion is true if the total height is greater than equal to the
    entered value.

Length
------

Description
^^^^^^^^^^^

Provides some tests against the maximal length of all products within the cart.

Value
^^^^^

A number which describes a length level. How this is interpreted is up
to the used operator (see below).

Operators
^^^^^^^^^

Equal
    The criterion is true if the maximal length is equal to the entered value.

Less than
    The criterion is true if the maximal length is less than the entered value.

Less than equal to
    The criterion is true if the maximal length is less than equal to the
    entered value.

Greater than
    The criterion is true if the maximal length is greater than the entered
    value.

Greater than equal to
    The criterion is true if the maximal length is greater than equal to the
    entered value.

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

Weight
------

Description
^^^^^^^^^^^

Represents the total weight of all products within the cart.

Value
^^^^^

A number which describes a weight level. How this is interpreted is up to the
used operator (see below).

Operators
^^^^^^^^^

Equal
    The total weight is equal to the entered value

Less than
    The total weight is less than the entered value

Less than equal to
    The total weight is less than equal to the entered value

Greater than
    The total weight is greater than the entered value

Greater than equal to
    The total weight is greater than equal to the entered value

Width
-----

Description
^^^^^^^^^^^

Provides some tests against the maximal height of all products within the cart.

Value
^^^^^

A number which describes a width level. How this is interpreted is up to the
used operator (see below).

Operators
^^^^^^^^^

Equal
    The criterion is true if the maximum width is equal to the entered value.

Less than
    The criterion is true if the maximum width is less than the entered value.

Less than equal to
    The criterion is true if the maximum width is less than equal to the
    entered value.

Greater than
    The criterion is true if the maximum width is greater than the entered
    value.

Greater than equal to
    The criterion is true if the maximum width is greater than equal to the
    entered value.
