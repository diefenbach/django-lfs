.. index:: Customer, Shipping Address, Invoice Address

=========
Customers
=========

This section describes the management interface for customers (``Customers / Customers``). LFS creates a customer
for every visitor who puts something into the cart; registered customers have a user account.

.. image:: /images/manage_customers.png
   :alt: The list of customers

List
====

The list shows the customers with ``ID``, ``Name``, ``Email``, number of ``Orders``, ``Cart Value`` and ``Date
Joined``. Click a column heading to sort by it, and a customer to see the details.

Filter
    Filter by name (first or last name of the customer's addresses) and by the date with ``Start`` and ``End`` or
    the buttons ``Today``, ``Week`` and ``Month``. Click ``Apply`` to filter and ``Reset`` to show all customers
    again.

Details
=======

The detail page of a customer shows:

* Customer information: name, e-mail, user account.
* Shipping and invoice address.
* The orders of the customer; click one to open it.
* The current cart with its items, if there is one.

``All Customers`` leads back to the list.

.. note::

    Customers who did not register and have neither a cart nor an order are removed by the management command
    ``cleanup_customers``, see :doc:`/developer/management_commands`.
