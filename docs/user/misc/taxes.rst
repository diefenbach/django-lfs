.. index:: Taxes

.. _general-taxes:

=====
Taxes
=====

This section describes how LFS handles taxes.

General
=======

There are two types of taxes within LFS: ``Product taxes`` and ``Customer taxes``:

* Product taxes define the default tax for a product and are used to calculate
  the default net or gross price. Which one depends on the type of price you
  have entered for your product. This taxes are assigned directly on the
  product within the product's management interface.

* Customer taxes define the tax for a specific customer, for instance in which
  country the product is delivered. These taxes are entered on the Customer
  Taxes management interface within the Shop menu.

.. Note::

      If you don't have different taxes based on customers you can safely
      ignore the rest of this document.

Calculating taxes
=================

Following we'll explain how LFS calculates taxes.

Example 1
---------

* Let's say you have entered the price of a product **inclusive tax**, i.e.
  the gross price of the product or in other words your selected **Price
  calculator** is **Price includes tax**.

* LFS will calculate the **net price** of the product on base of the
  **Product tax** (the tax you have assigned to the product).

* LFS will then calculate the product's gross price for a customer on base of
  the **customer tax** which you have entered for the country of the customer's
  shipping address. If there is no customer tax for the customer in question
  LFS falls back to the product tax in order to calculate the gross price.

Example 2
---------

* Now let's imagine you have entered the price of the product **exclusive tax**,
  i.e. the **net price** of the product. or in other words your selected
  **Price calculator** is **Price excludes tax**.

* LFS will just take the price you have entered for the product and calculates
  the product's gross price on base of the **customer tax** which you have
  entered for the country of the customer's shipping address. If there is no
  customer tax for the customer in question LFS falls back to the product tax
  in order to calculate the gross price.

Conclusion
==========

In both examples you see that the product tax is used when no customer tax is
found. This means if you don't have the need for different taxes based on
customers you can safely ignore them at all and just assign your default taxes
directly to the products.

.. seealso::

    * :ref:`Manage product taxes <management-taxes>`
    * :ref:`Manage customer taxes <management-customer-taxes>`
