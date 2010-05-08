.. index:: Shipping method, Shipping methods

.. _management-shipping-methods:

================
Shipping methods
================

This section describes the shipping methods management of LFS.

Overview:
=========

* You can add as many shipping methods you want.

* All valid shipping methods are displayed for selection to the shop customer.
  
* A shipping method is true if all criteria of the shipping method are true.

* Shipping methods can have many prices which are dependent of criteria. The
  first price which is valid (all criteria are true) is the current price for
  the for the shipping method. If no price is valid the default price is taken
  (from data tab).

Data
====

Name
    The name of the shipping method, which is displayed to the shop 
    customer.

Description
    A short description of the shipping method, which is also displayed 
    to the customer.

Note 
    A note of the shipping method, which is displayed on the confirmation
    mail after the shop customer has been checked out.

Priority
    The first valid shipping method with the highest priority (smaller 
    number) method is displayed to the customer.

Image
    An image for the shipping method, which is displayed to the shop 
    customer.

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

Prices
======

**To add a price proceed as following**:

1. To manage prices go to the *Prices*-tab.
2. To add a new price enter the value into the text field and click *Add price*.
3. To add/edit criteria for that price click on *Edit criteria*. A popup will open.
4. Click on *Add criteria* and change the criteria type, the operator and
   the value of the criteria to your needs.

**To update/delete a price proceed as following**:

* To update the prices change the priority and/or the value of the price and 
  click on *Update prices*.
* To delete the prices select the checkboxes of the prices you want delete 
  and click on *Delete prices*.

.. seealso::

    * :ref:`How to manage shipping methods <howto-shipping-methods>`