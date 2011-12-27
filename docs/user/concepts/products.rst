.. index:: Product

.. _products_concepts:

========
Products
========

This section describes the products of LFS.

Overview
========

Products are provided for sale to the shop customer. Products are the central
content object within LFS. All attributes of a product is managed here. For
instance the prices, stock data, images and attachements. Please refer to the
:doc:`product management interface </user/management/catalog/products>` to see
all attributes of a product.

.. _product-types-label:

Types
=====

There are four types of products: product, configurable product,
product with variants and variant.

.. index:: single: Product; Default

.. _products_concepts_product:

Product
-------

The plain default product of LFS. This is in some way the base of all other
product types which are described in the following sections.

.. index:: single: Product; Configurable

.. _products_concepts_configurable_product:

Configurable Product
--------------------

A configurable product is a product with several properties (e.g. color) and
options (e.g. red, green, blue) from which a shop customer can choose. The
provided properties and options can optionally change the total price of the
configurable product. That is usually calculated by the product's base price
plus all selected options of its properties.

.. seealso::

    * :doc:`/user/howtos/how_to_configurable_product`

.. index:: single: Product; with Variants

.. _products_concepts_product_with_variants:

Product With Variants
---------------------

A product with variants consists of two parts: A ``product with variants``
and the ``variants`` (see below).

The ``product with variants`` can be considered as the parent of its
``variants``, which can't be sold. It is just a container for the variants and
provides default data which can be inherited by the variants. The ``product with
variants`` uses :doc:`global <properties>` and :doc:`local properties
<local_properties>` to create the variants.

.. seealso::

    * :doc:`/user/howtos/how_to_variants`


.. index:: single: Product; Variant

.. _products_concepts_variant:

Variant
-------

This is a single variant of a ``product with variants``, which can be sold to
the customer. By default a variant inherits all data of the parent ``product
with variants``. A ``variant`` can overwrite the data from the belonging parent.
A variant belongs to a unique combination of properties. The properties are
defined by the ``product with variants``.

See Also
========

* :doc:`Product Management Interface </user/management/catalog/products>`
