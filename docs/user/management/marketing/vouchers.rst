.. index:: Voucher, Voucher Group

.. _vouchers_management:

========
Vouchers
========

This section describes the management interface for vouchers (``Marketing / Vouchers``). Vouchers are created in
voucher groups, e.g. one group per campaign.

Site actions
============

Add Voucher Group
    Adds a voucher group.

Delete Voucher Group
    Deletes the selected voucher group with its vouchers, after a confirmation.

Tabs
====

Data
----

Name
    The name of the voucher group, for internal use only. Click ``Save voucher group`` to save it.

Vouchers
--------

Add New Vouchers
    Fill in the form and click ``Add vouchers``:

    Amount
        How many vouchers to create.

    Value
        The value of each voucher, an amount or a percentage depending on ``Kind of``.

    Start date / End date
        The period in which the vouchers can be redeemed.

    Kind of
        ``Absolute`` or ``Percentage``.

    Effective from
        The minimum price of the products in the cart (without shipping and payment) from which the vouchers can be
        redeemed.

    Tax
        The tax of the vouchers; leave it empty if you do not know it.

    Limit
        How often each voucher can be redeemed.

    Sums up
        Whether the vouchers can be combined with discounts. LFS adds up all discounts and vouchers that sum up,
        takes the highest one that does not, and gives the higher of the two.

Existing Vouchers
    Lists the vouchers of the group with their numbers. Search them by number and filter them by usage (``All
    vouchers``, ``Used vouchers``, ``Unused vouchers``); select vouchers and click ``Delete selected vouchers`` to delete them.

Options
-------

The format of the voucher numbers. It applies to all voucher groups, and only to vouchers created afterwards.
Click ``Save voucher options`` to save it.

Number prefix
    The prefix of the voucher number: PREFIX-xxxxx.

Number suffix
    The suffix of the voucher number: xxxxx-SUFFIX.

Number length
    The length of the random part of the voucher number.

Number letters
    The characters the random part is made of.

See Also
========

* :ref:`Vouchers in General <marketing_concepts_vouchers>`
