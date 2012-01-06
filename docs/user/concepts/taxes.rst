.. index:: Taxes

.. _taxes_concept:

=====
Taxes
=====

This section describes how LFS calculates taxes.

.. Note::

      If you don't have different taxes based on customers you can safely
      ignore the rest of this section.

Overview
========

There are two types of taxes: product taxes and customer taxes.

``Product taxes`` define the default tax for a product and are used to calculate
the default net or gross price of a product. Which one of these depends on the
type of price you have entered for your product. Product taxes are are assigned
directly on the product.

``Customer taxes`` define the tax for a specific customer respective for the
country in which the goods are to be delivered. These taxes are managed
centrally and selected automatically by LFS for the calculation.

Calculating Taxes
=================

Following we'll explain how LFS calculates taxes.

Example 1
---------

Assuming that the  entered price of a product is inclusive tax, i.e. the entered
price is the gross price of the product or in other words the selected ``Price
calculator`` of the product is ``Price Includes Tax``.

LFS will calculate the net price of the product on base of the entered Product
tax, the tax you have assigned to the product.

LFS will then calculate the product's gross price for a customer on base of the
customer tax which you have entered for the country of the customer's shipping
address. If there is no customer tax for the customer LFS falls back to the
product tax in order to calculate the gross price.

Example 2
---------

Now let's imagine you have entered the price of the product exclusive tax, i.e.
the net price of the product, or in other words the selected ``Price
calculator`` of the product is ``Price Excludes tax``.

LFS will just take the entered price for the product and calculates the
product's gross price on base of the customer tax which you have entered for the
country of the customer's shipping address. If there is no customer tax for the
customer LFS falls back to the product tax in order to calculate the gross
price.

Conclusion
==========

In both examples you see that the product tax is used when no customer tax is
found. This means if you don't have the need for different taxes based on
customers you can safely ignore them at all and just assign your default taxes
directly to the products.

See Also
========

* :ref:`Manage product taxes <product_taxes_management>`
* :ref:`Manage customer taxes <management-customer-taxes>`
