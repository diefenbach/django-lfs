========
Products
========

This section describes all product types in detail.

Overview
========

* Products are sold to the shop customer.
* Products can belong to an arbitrary amount of categories.
* Products can have an arbitrary amount of images.
* Products can have an arbitrary amount of attachements.
* Products can have :term:`portlets`.

.. _product-types-label:

Types
=====

There are four types of products: product, configurable product,
product with variants and variant. Following there are described in
more detail.

.. _product-product-label:

Product
-------

The plain default product of LFS.

.. _product-configurable-product-label:

Configurable product
--------------------

* A configurable product is a product with several properties which can be
  changed by the shop customer.

* Properties can have different types, e.g. selection field, number field or
  text field. Based on this type the shop customer can enter values to this
  fields.

* Properties can optionally change the price of the product.

* The price of an configurable product is usually calculated by the product"s
  base price plus all selected/entered values of its properties

.. _product-product-with-variant-label:

Product with variants
---------------------

* A product with variants consists of two parts: A "product with variants"
  and the variants.

* The "product with variants" can be considered as the parent of its variants.

* The parent can't be sold. It is just a container for the variants and provides
  default data which can be inherited by the variants.

* The parent has/defines some properties (global or local) which are the base
  to create the variants.

.. _product-variant-label:

Variant
-------

This is a single variant of a Product with variants.

* A variant can be sold to the customer.

* By default a variant inherits all data of the parent "product with variants".

* A variant can overwrite the data from the belonging parent product. To do
  that the fields in question have to be activated explicitly.

* A variant belongs to a unique combination of properties. The properties are
  defined by the "product with variants".

.. seealso::

    * :doc:`Product management interface </user/catalog/products>`
