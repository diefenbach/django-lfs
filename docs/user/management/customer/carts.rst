.. index:: Cart, Carts

=====
Carts
=====

This section describes the management interface for carts (``Customers / Carts``): the carts of customers that
have not (yet) become orders.

List
====

The list shows the carts with ``Cart ID``, ``Customer`` (or ``Anonymous``), ``Products``, ``Items``, ``Total`` and
``Modified``. Click a cart to see its details.

Filter
    Filter by the date of the last change with ``Start`` and ``End`` or the buttons ``Today``, ``Week`` and
    ``Month``. Click ``Apply`` to filter and ``Reset`` to show all carts again.

Details
=======

The detail page of a cart shows its customer and its items with product, quantity, price and total.

All Carts
    Back to the list.

Delete Cart
    Deletes the cart with all its items, after a confirmation.

.. note::

    Carts that have not been changed for 7 days are removed by the management command ``cleanup_carts``, see
    :doc:`/developer/management_commands`.
