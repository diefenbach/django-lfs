.. index:: Property Group

.. _property_groups_management:

===============
Property Groups
===============

This section describes the management interface for property groups (``Properties / Property Groups``). A property
group bundles properties; products get the properties of the groups they belong to.

Site Actions
============

Add Property Group
    Adds a property group.

Delete Property Group
    Deletes the selected property group, after a confirmation.

    .. warning::

        All values assigned to products for the properties of this group get lost.

Tabs
====

Data
----

Name
    The unique name of the property group, used to assign it to products.

Click ``Save property group`` to save the changes.

Products
--------

The products of the group get all its properties.

Add products
    In the section ``Available Products`` (searchable by name, filtered by category) select the products
    and click ``Add to Property Group``.

Remove products
    In the section ``Assigned Products`` select the products and click ``Remove from Property Group``.

    .. warning::

        The values of the group's properties on these products get lost.

Properties
----------

Add properties
    In the section ``Available Properties`` (searchable by name, filtered by type) select the properties and click
    ``Add to Property Group``.

Sort properties
    Drag a property in the section ``Assigned Properties`` by its handle in the ``Sort`` column.

Remove properties
    In the section ``Assigned Properties`` select the properties and click ``Remove from Property Group``.

    .. warning::

        The values of the removed properties on the group's products get lost.

The values of the properties are entered per product, on the :ref:`Properties tab of the product
<products_management_properties>`.

See also
========

* :ref:`Properties within Product Management Interface <products_management_properties>`
