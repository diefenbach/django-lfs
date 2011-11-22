.. index:: Payment method, Payment methods

.. _management-payment-methods:

===============
Payment methods
===============

This section describes the shipping methods management of LFS.

Overview
========

* You can add as many payment methods as you want.

* All valid payment methods are displayed for selection to the shop customer.

* A payment method is valid if all criteria of the shipping method are true.

* Payment methods can have many prices which are dependent of criteria. The
  first price which is valid (all criteria are true) is the current price for
  the the payment method. If no price is valid the default price is taken
  (from data tab).

Data
====

Name
    The name of the payment method, which is displayed to the shop
    customer (e.g. on the cart and the checkout page).

Description
    A short description of the payment method, which is displayed to the
    customer (e.g. on the checkout page).

Note
    A note of the payment method, which is displayed on the confirmation
    mail after the shop customer has been checked out.

Priority
   The first valid shipping method with the highest priority (smaller
   number) method is displayed to the customer as default (if she hasn't
   selected one explicitly).

Image
    An image for the payment method, which is displayed to the shop
    customer.

Tax
    The included tax of the payment method's price

Price
    The default price of the payment method. This can be overwritten
    within the price tab (see below).

Module
    The dotted name of the external package which processes the payment
    (this is for developers only).

Type
    The type of the payment method. Dependent on that additional fields
    for input (within the checkout process) will be displayed. There are
    three types at the moment:

      * Plain
        No additional fields are displayed.

      * Bank
        Fields for a bank account are displayed.

      * Credit Card
        Fields for a credit card are displayed.

Criteria
========

Optional you can add some criteria to the payment method. Only when all
criteria are true the payment method is displayed to the shop customer. See
:doc:`/user/misc/criteria` for more.

**To add criterion proceed as following:**

* Click on the ``Add criteria``-button (adds a criterion on first position) or
  on the ``plus`` button beside a criterion (adds a criterion below)
* Select the criteria type you want, e.g. ``Weight`` (this is the weight of
  all cart items).
* Select the operator, e.g. ``Less than equal to``.
* Enter the value, e.g. 50.
* Altogether this means the payment method is valid if the weight of all
  cart items is less than or equal to 50 units.
* You can add as many criteria you want.
* Click on ``Save criteria``.

**To update criteria proceed as following:**

* Change the values of the criteria to your needs.
* Click on ``Save criteria``

**To delete a criterion proceed as following:**

* Click on the ``minus`` button beside the criterion.
* Click on ``Save criteria``.

Prices
======

Optionally payment methods can have different prices based on criteria. If
no prices are given within the prices tab, the default price of the data tab
is taken.

.. image:: /images/how_to_payment_prices.*

**To add a price proceed as following:**

* To manage prices go to the ``Prices`` tab.
* To add a new price enter the value into the text field and click ``Add
  price``.
* To add/edit criteria for that price click on ``Edit criteria`` link. A popup
  will open.
* Click on ``Add criteria`` and change the criteria type, the operator and
  the value to your needs.

**To update/delete a price proceed as following:**

* To update the prices change the priority and/or the value of the price and
  click on ``Update prices``.
* To delete the prices select the checkboxes of the prices you want delete and
  click on ``Delete prices``.

.. seealso::

    * :ref:`How to manage payment methods <howto-payment-methods>`
