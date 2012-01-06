.. index:: Voucher, Voucher Group

.. _vouchers_management:

========
Vouchers
========

This section describes the management interface for vouchers.

Site actions
============

Add Voucher Group
    Adds a new voucher group to the shop.

Delete Voucher Group
    Deletes the currently displayed voucher group.

Tabs
====

Data
----

Within the data tab you can change the name of the voucher group.

Name
    The name of the voucher group (this is just for internal usage).
Position
    Voucher groups are ordered by position, lower number comes first.

Vouchers
--------

Within the vouchers tab you can manage the vouchers of the current voucher
group.

Amount
    The amount of voucher which are supposed to be created.

Value
    The value of the voucher. This is either an absolute or an percentage
    value dependent on the type of the voucher (see below).

Start/End:
    The range when the vouchers are valid.

Kind of:
    The type of the voucher. Either absolute or percentage.

Effective from:
    The minimum cart price from which the voucher are valid. This is only the
    total cart item prices without shipping and payment costs.

Tax
    The tax of the vouchers. If you don't know the tax just let it empty.

Limit
    Determines how often the vouchers can be used.

Add Vouchers
^^^^^^^^^^^^

In order to add vouchers, fill in the provided form and click on ``Add
Vouchers``.

Delete Vouchers
^^^^^^^^^^^^^^^

To delete vouchers check all voucher you want to delete and click on ``Delete
Vouchers``.

Options
-------

Within the options tab you can change the options for voucher numbers.

Number prefix
    The prefix of the voucher number: PREFIX-xxxxx.

Number suffix
    The suffix of the voucher number: xxxxx-SUFFIX.

Number length
    The length of the voucher number.

Number letters
    The used letters to create a voucher number

.. note::

    The current options are only effective for upcoming vouchers.

See Also
========

* :ref:`Vouchers in General <marketing_concepts_vouchers>`

