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
  have entered for your product. This taxes are selected on the product.

* Customer taxes define the tax for a specific customer, for instance in which
  country the product is delivered This taxes are entered on Shop / Customer Taxes.
  management interface.

  .. Note::

      If you don't have different taxes based on customers you can safely
      ignore this type of taxes (for instance if you just sell products within
      Germany.)

Using taxes
===========

Following we'll explain how LFS calculates taxes.

Example 1
---------

Let's say you have entered the price of a product inclusive tax (in other words
your selected "Price calculator" is "Price excludes tax").

LFS will calculated the net price on base of the "Product tax" (the tax you
have selected on the product.)

LFS will then calculate the gross price for the product on base of the customer
tax that you have entered for the country of the customer's shipping address.
If there is no customer tax for the customer in question LFS uses the product
tax in order to calculate the gross price.


Example 2
---------

Now let's imagine you have entered the price of the product exclusive tax
(in other words your selected "Price calculator" is "Price includes tax").

LFS will just take the price you have entered for the product an calculates
the tax on base of the customer tax that you have entered for the country
of the customer's shipping address. If there is no customer tax for the
customer in question LFS uses the product tax in order to calculate the gross
price.

Conclusion
==========

In this both examples you will see that the product tax is used when no
customer tax is found. This means if you don't have the need for different
taxes based on customers you can safely ignore them at all and just add your
country specific taxes to the products.

.. seealso::

    * :ref:`Manage product taxes <management-taxes>`
    * :ref:`Manage customer taxes <management-customer-taxes>`
