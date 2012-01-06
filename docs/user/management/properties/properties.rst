.. index:: Property

.. _properties_management:

==========
Properties
==========

This section describes the management interface for properties.

Site Actions
============

Add Property
    Adds a new property.

Delete Property
    Deletes the current displayed property.

    .. warning::

        Please note that all values which have been assigned to products for
        this property will get lost.

Data
====

Position
    The position within the product.

Name
    The unique name of the property. This is displayed within the management
    interface to select the property for several purposes.

Title
    The title of the property. This is displayed to the shop customer.

Filterable
    If this is checked the property will be displayed for filtering (within
    the filter :term:`portlet`).

Display no results
    If this is checked filter ranges with no products will be displayed within
    the filter portlet. Otherwise they will be removed. This is only displayed
    if ``Filterable`` is checked.

Display on product
    If this is checked the property will be displayed on the product.

Configurable
    If this is checked the property will be displayed for selection/input on
    a configurable product

Required
    If this is checked the property must be selected/entered on a configurable
    product. This is only displayed if ``Configurable`` is checked.

Unit
    The unit of the property, e.g. meter, liter or whatever you want. This is
    just a simple string without logic.

Field type
    The field type of the property. Based on the type of the field you need
    to provide additional data. See :ref:`Properties in general
    <properties_concepts_types>` for more information.

See also
=========

* :ref:`Properties in general <properties_concepts>`
* :ref:`Property Groups Management Interface <property_groups_management>`
