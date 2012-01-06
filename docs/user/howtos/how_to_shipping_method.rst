.. index:: Shipping Method

.. _shipping_methods_howto:

==============================
How To Manage Shipping Methods
==============================

Overview
========

In this how-to you will learn how to add and edit shipping methods and how to
add criteria and prices for them.

.. include:: /includes/demo_shop.rst

Get Started
===========

In order to add/edit a shipping method please go to Management / Shop /
Shipping Methods.

.. image:: /images/how_to_shipping_manage.*

If there are no shipping methods yet, you will automatically get to the add
shipping method form. Otherwise the first shipping method is displayed and
you can click on a shipping method to edit this or on ``Add shipping method``
to add a new one.

.. image:: /images/how_to_shipping_add.*

If you have done that you can edit or enter the data for a shipping method as
described below.

Data
====

The data tab contains all core data for the shipping method.

.. image:: /images/how_to_shipping_data.*

* Now fill in the fields:

    * **Name:** The name of the shipping method, which is displayed to the
      shop customer.
    * **Description:** A short description of the shipping method, which is also
      displayed to the customer.
    * **Note:** A note of the shipping method, which is displayed on the confirmation
      mail after the shop customer has been checked out.
    * **Priority:** The first valid shipping method with the highest priority
      (smaller number) method is displayed to the customer.
    * **Image:** An image for the shipping method, which is displayed to the
      shop customer.
    * **Tax:** The included tax of the shipping method's price.
    * **Price:** The default price of the shipping method. This can be
      overwritten within the price tab (see below).

* Click on ``Save``-button

.. _how_to_shipping_method_criteria:

Criteria
========

Optional you can add some criteria to the shipping method. Only when all
criteria are true the shipping method is displayed to the shop customer.

.. image:: /images/how_to_shipping_criteria.*

**To add criterion proceed as following:**

* Click on the ``Add criteria``-button (adds a criterion on first position) or on the
  ``plus`` button beside a criterion (adds a criterion below)
* Select the criteria type you want, e.g. ``Weight`` (this is the weight of all cart items).
* Select the operator, e.g. ``Less than equal to``.
* Enter the value, e.g. 50.
* Altogether this means the shipping method is valid if the weight of all
  cart items is less than or equal to 50 units.
* You can add as many criteria you want.
* Click on ``Save criteria``.

**To update criteria proceed as following:**

* Change the values of the criteria to your needs.
* Click on ``Save criteria``

**To delete a criterion proceed as following:**

* Click on the ``minus`` button beside the criterion.
* Click on ``Save criteria``.

.. _how_to_shipping_method_prices:

Prices
======

Optional you can add additional prices to the shipping method and restrict them
with criteria. The first price which meets all criteria will be taken.

.. image:: /images/how_to_shipping_prices.*

**To add a price proceed as following:**

* To manage prices go to the ``Prices`` tab.
* To add a new price enter the value into the text field and click ``Add price``.
* To add/edit criteria for that price click on ``Edit criteria`` link. A pop-up
  window will open.
* Click on ``Add criteria`` and change the criteria type, the operator and
  the value to your needs.

**To update/delete a price proceed as following:**

* to update the prices change the priority and/or the value of the price and click on ``Update prices``.
* To delete the prices select the check boxes of the prices you want delete and click on ``Delete prices``.

See Also
========

* :ref:`Manage shipping methods <shipping_methods_management>`
