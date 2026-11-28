.. index:: Order, Orders

======
Orders
======

This section describes the management interface for orders (``Customers / Orders``).

.. image:: /images/manage_orders.png
   :alt: The list of orders with the filter on the left

List
====

The list shows all orders, the newest first, with ``Order ID``, ``Customer``, ``Created`` and ``State``. Click an
order to see its details.

Filter
    Filter by customer name (first or last name), ``State`` and payment method, and by the date with ``Start`` and
    ``End`` or the buttons ``Today``, ``Week`` and ``Month``. Click ``Apply`` to filter and ``Reset`` to show all
    orders again.

Details
=======

The detail page of an order shows:

* General information: number, customer, e-mail, phone, date, state, total.
* Addresses & Methods: shipping and invoice address, shipping and payment method, and for direct debit the bank
  account.
* Order items with image, SKU, name, amount, price, VAT and total, and a voucher if one was used.
* The message the customer wrote in the checkout, if any, and for PayPal the transaction id.

Actions
-------

All Orders
    Back to the list.

Change state
    Select the new ``State`` and click ``Change``. The states are ``Submitted``, ``Paid``, ``Prepared``, ``Sent``,
    ``Closed``, ``Canceled``, ``Payment Failed`` and ``Payment Flagged``.

Resend Order
    Sends the order confirmation to the customer again, after a confirmation.

Delete Order
    Deletes the order, after a confirmation.
