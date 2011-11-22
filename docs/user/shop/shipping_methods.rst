.. index:: Shipping method, Shipping methods

.. _management-shipping-methods:

================
Shipping methods
================

This section describes the shipping methods management of LFS.

Overview:
=========

* You can add as many shipping methods as you want.

* All valid shipping methods are displayed for selection to the shop customer.

* A shipping method is valid if all criteria of the shipping method are true.

* Shipping methods can have many prices which are dependent of criteria. The
  first price which is valid (all criteria are true) is the current price for
  the shipping method. If no price is valid the default price is taken (from
  data tab).

Data
====

Name
    The name of the shipping method, which is displayed to the shop
    customer (e.g. on the cart and the checkout page).

Description
    A short description of the shipping method, which is displayed to the
    customer (e.g. on the checkout page).

Note
    A note of the shipping method, which is displayed on the confirmation
    mail after the shop customer has been checked out.

Priority
    The first valid shipping method with the highest priority (smaller
    number) method is displayed to the customer as default (if she hasn't
    selected one explicitly).

Image
    An image for the shipping method, which is displayed to the shop
    customer (On the checkout page).

Tax
    The included tax of the shipping method's price.

Price
    The default price of the shipping method. This can be overwritten
    within the price tab (see below).

Delivery time
    The delivery time of the shipping method. See :doc:`delivery_times`.

Criteria
========

The criteria of the discount. The shipping method is displayed for selection
if all criteria are true. See :doc:`/user/misc/criteria` for more.

**To add criterion proceed as following:**

* Click on the ``Add criteria``-button (adds a criterion on first position) or
  on the ``plus`` button beside a criterion (adds a criterion below)
* Select the criteria type you want, e.g. ``Weight`` (this is the weight of
  all cart
  items).
* Select the operator, e.g. ``Less than equal to``.
* Enter the value, e.g. 50.
* Altogether this means the shippping method is valid if the weight of all
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

Optionally shippping methods can have different prices based on criteria. If
no prices are given within the prices tab, the default price of the data tab
is taken.

**To add a price proceed as following**:

* To manage prices go to the ``Prices`` tab.
* To add a new price enter the value into the text field and click ``Add
  price``.
* To add/edit criteria for that price click on ``Edit criteria`` link. A popup
  will open.
* Click on ``Add criteria`` and change the criteria type, the operator and
  the value to your needs.

**To update/delete a price proceed as following**:

* To update the prices change the priority and/or the value of the price and
  click on *Update prices*.
* To delete the prices select the checkboxes of the prices you want delete
  and click on *Delete prices*.

.. seealso::

    * :ref:`How to manage shipping methods <howto-shipping-methods>`
