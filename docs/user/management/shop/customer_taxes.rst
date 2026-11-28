.. index:: Customer Tax
    single: Tax; Customer

.. _management-customer-taxes:

==============
Customer Taxes
==============

This section describes the management interface for customer taxes (``Shop / Customer Taxes``): tax rates that
apply instead of the product tax when their criteria are met, for instance for customers from another country.

Site Actions
============

Add Customer Tax
    Opens a dialog to add a customer tax with its ``Rate`` and ``Description``.

Delete Customer Tax
    Deletes the selected customer tax, after a confirmation.

Tabs
====

Data
----

Rate
    The tax rate in percent.

Description
    A short description for internal use only.

Click ``Save Customer Tax`` to save the changes.

Criteria
--------

The customer tax applies when all its criteria are met, e.g. a ``Country`` criterion for the countries it is valid
for. Click ``Add criterion``, select the type, operator and value of each criterion, and click ``Save criteria``.

See also
========

* :ref:`Taxes in general <taxes_concept>`
* :ref:`Criteria in general <criteria_concepts>`
* :ref:`Manage product taxes <product_taxes_management>`
