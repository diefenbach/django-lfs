.. index:: Product

.. _products_concepts:

========
Products
========

This section describes the different product types of LFS.

Overview
========

Products are the most essential content object of LFS. They are goods which are
sold to customers. LFS' products manage a lot of data
which are relevant for an online shop. Please see the :doc:`product management
interface reference </user/management/catalog/products>` to see all available
data fields in detail.

.. _product_types_label:

LFS provides  three types of products: default products, configurable products
and products with variants. They are described in more detail in the following
sections.

.. index:: single: Product; Default

.. _products_concepts_product:

Default Product
===============

This is the simple and straightforward product of LFS. All other product types
are based on the default product. It handles a lot of information like:

    * General descriptions
    * Prices and price units
    * Images
    * Attachments
    * :ref:`Accessories <marketing_concepts_accessories>`
    * :ref:`Related products <marketing_concepts_related_products>`
    * Stock data
    * SEO Data
    * :ref:`Portlets <portlets_concepts>`
    * :ref:`Properties <properties_concepts>`

Each of this is described in more detail throughout this documentation.

.. index:: single: Product; Configurable

.. _products_concepts_configurable_product:

Configurable Product
====================

A configurable product is a product with several properties and options from
which a customer can or needs to choose. For instance a property ``Color`` and
its options ``red``, ``yellow`` and ``green``. The selected options of the
properties can change the total price of the product, which is calculated by the
base price plus the prices of the selected options.

.. seealso::

    * :doc:`/user/howtos/how_to_configurable_product`

.. index:: single: Product; with Variants

.. _products_concepts_product_with_variants:

Product with Variants
=====================

A ``product with variants`` is a product from which the customer can choose out
of an arbitrary amount of similar variants. It consists out of two parts: the
base and the variants.

Base
----

The base can't be sold to customers, but it serves as a container for the
variants and provides default data, which can be inherited from the variants.

To create variants for a base :doc:`global <properties>` and :doc:`local
properties <local_properties>` are used, e.g. the property ``Color`` and its
options ``red``, ``yellow`` and ``green``. Each variant of a base belongs to a
unique combination of options of all properties of a base.

.. index:: single: Product; Variant

.. _products_concepts_variant:

Variant
-------

The variants can be sold to a customer. Each variant is a discrete product with
its own data, e.g. own price, name and SKU. By default the variants inherit all
data from the base. This data can be overwritten per variant and field.

.. seealso::

    * :doc:`/user/howtos/how_to_variants`

See Also
========

* :doc:`Product Management Interface </user/management/catalog/products>`
