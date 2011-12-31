.. index:: Product

.. _products_concepts:

========
Products
========

This section describes the concepts of products.

Overview
========

Products are the central content object of LFS. These are provided for sale to
the customer. Almost all relevant attributes of products are entered here, for
instance the price, stock data, images and attachments. More details about all
attributes can be found at :doc:`product management interface reference
</user/management/catalog/products>`.

.. _product-types-label:

Types
=====

There are three types of products: default products, configurable products and
products with variants.

.. index:: single: Product; Default

.. _products_concepts_product:

Product
-------

This is the plain default product of LFS and can be considered as the the base
of all other product types, which are described in the following sections.

.. index:: single: Product; Configurable

.. _products_concepts_configurable_product:

Configurable Product
--------------------

A configurable product is a product with several properties and options from
which a customer can or has to choose. For instance the property ``Color`` and
its option ``red, yellow and green``. The selected options of all properties can
change the total price of the product. This is calculated by the base price of
the product plus all selected options of all provided product's properties.

.. seealso::

    * :doc:`/user/howtos/how_to_configurable_product`

.. index:: single: Product; with Variants

.. _products_concepts_product_with_variants:

Product with Variants
---------------------

A ``product with variants`` is a product from which the customer can choose out
of an arbitrary amount of similar variants.

The most essential difference to a ``configurable product`` is, that every
variant is a discrete product with own data, like the price or the article
number - whereas the latter can be important for accounting.

Technical the ``product with variants`` consists out of two parts: the base and
its variants.

Base
^^^^

The base can be considered as the parent of the variants. It can't be sold to
customers, but it serves as a container for the variants and provides default
data, which can be inherited from the variants.

To create variants for a base :doc:`global <properties>` and :doc:`local
properties <local_properties>` are used. Each variant belongs then to a
unique combination of options from all properties.

.. index:: single: Product; Variant

.. _products_concepts_variant:

Variant
^^^^^^^

This is a single variant of a ``product with variants``. Variants can be offered
for sale. By default the variants inherit all data from the base, but this data
can be overwritten per variant and per field. This can be considered as the most
essential difference to a ``configurable product``. For example each variant can
have an own price or an own article number. Latter can be important for
accounting.

.. seealso::

    * :doc:`/user/howtos/how_to_variants`

See Also
========

* :doc:`Product Management Interface </user/management/catalog/products>`
