.. index:: Payment method

.. _payment_methods_howto:

=============================
How To Manage Payment Methods
=============================

Overview
========

In this how-to you will learn how to add and edit payment methods and how to
add criteria and prices for them.

.. include:: /includes/demo_shop.rst

Get started
===========

In order to add/edit a payment method please go to Management / Shop /
Payment Methods.

.. image:: /images/how_to_payment_manage.*

If there are no payment methods yet, you will automatically get to the add
payment method form. Otherwise the first payment method is displayed and
you can click on a payment method to edit this or on ``Add payment method``
to add a new one.

If you have done that you can edit or enter the data for a payment method as
described below.

Data
====

The data tab contains all core data for the payment method.

.. image:: /images/how_to_payment_data.*

Now fill in the fields:

* **Name:** The name of the payment method, which is displayed to the
  shop customer.

* **Description:** A short description of the payment method, which is also
  displayed to the customer.

* **Note:** A note of the payment method, which is displayed on the
  confirmation mail after the shop customer has been checked out.

* **Priority:** The first valid payment method with the highest priority
  (smaller number) method is displayed to the customer.

* **Image:** An image for the payment method, which is displayed to the
  shop customer.

* **Tax:** The included tax of the payment method's price.

* **Price:** The default price of the payment method. This can be
  overwritten within the price tab (see below).

* **Module:** The dotted name of the external package which processes the
  payment (this is for developers only).

* **Type:** The type of the payment method. Dependent on that additional
  fields for input (within the checkout process) will be displayed. There
  are three types at the moment:

    * **Plain**
      No additional fields are displayed.

    * **Bank**
      Fields for a bank account are displayed.

    * **Credit Card**
      Fields for a credit card are displayed.

And click on the ``Save``-button.

.. _how_to_payment_method_criteria:

Criteria
========

Optional you can add some criteria to the payment method. Only when all
criteria are true the payment method is displayed to the shop customer.

.. image:: /images/how_to_payment_criteria.*

**To add criterion proceed as following:**

* Click on the ``Add criteria``-button (adds a criterion on first position) or on the
  ``plus`` button beside a criterion (adds a criterion below)
* Select the criteria type you want, e.g. ``Weight`` (this is the weight of all cart items).
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

.. _how_to_payment_method_prices:

Prices
======

Optional you can add additional prices to the payment method and restrict them
with criteria. The first price which meets all criteria will be taken.

.. image:: /images/how_to_payment_prices.*

**To add a price proceed as following:**

* To manage prices go to the ``Prices`` tab.
* To add a new price enter the value into the text field and click ``Add price``.
* To add/edit criteria for that price click on ``Edit criteria`` link. A pop-up
  window will open.
* Click on ``Add criteria`` and change the criteria type, the operator and
  the value to your needs.

**To update/delete a price proceed as following:**

* To update the prices change the priority and/or the value of the price and click on ``Update prices``.
* To delete the prices select the check boxes of the prices you want delete and click on ``Delete prices``.

See also
========

* :ref:`Manage payment methods <payment_methods_management>`
