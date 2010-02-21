========
Products
========

Products are saled to the shop customer.

Types
=====

There are three types of products:

Product
-------

This is the default product of LFS. Just enter the appropriate data, set it 
to active and the product is ready vor sale.

Product with variants
---------------------

A product with variants consists of two parts: ``Product with variant``-type 
(parent) and the ``Variant``-type (variants).

The parent can't be saled. It is just a container for the variants and provides 
default data which can be inherited by the variants.

The parent has/defines some ``Properties`` (global or local) which are the base
to create some ``Variants``.

Variant
-------

This is a single variant of a ``Product with variants``. 

* A variant can be saled to the customer.

* By default a variant inherits all data of the related ``Product with 
  variants``.
  
* A variant can overwrite the data from the belonging parent product. To do 
  that the fields in question have to be activated explicitely.

* A variant belongs to a unique combination of properties. The properties are 
  defined by the ``Product with variants``.