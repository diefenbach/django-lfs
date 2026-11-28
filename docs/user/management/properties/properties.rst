.. index:: Property

.. _properties_management:

==========
Properties
==========

This section describes the management interface for properties (``Properties / Properties``).

On the left are all properties (searchable by name), on the right the selected property.

.. image:: /images/manage_property_data.png
   :alt: The Data tab of a property

Site Actions
============

Add Property
    Adds a property.

Delete Property
    Deletes the selected property, after a confirmation.

    .. warning::

        All values assigned to products for this property get lost.

Data
====

Name
    The unique name of the property, used in the management interface to select it.

Title
    The title of the property, displayed to customers.

Unit
    The unit of the property, e.g. ``cm`` or ``kg``. It is displayed after the value; LFS does not calculate with
    it.

For Variants
    If checked, the property can be used to create variants. Only select fields can be used for variants.

Filterable
    If checked, the property is offered in the filter of the shop.

Configurable
    If checked, customers select or enter a value for the property on a configurable product.

Required
    If checked, customers must select or enter a value on a configurable product.

Display on product
    If checked, the property is displayed on the product page.

Click ``Save property`` to save the changes.

Field Type
==========

Type
    ``Text field``, ``Float field`` (a number) or ``Select field``. See :ref:`Properties in general
    <properties_concepts_types>`. Changing the type deletes all values of the property on products.

Select field
    Options
        Add an option with its ``Name`` and ``Price`` and click ``Add``; change the options and click ``Update
        options``.

    Display price
        If checked, the price of an option is displayed next to it on a configurable product.

    Add price
        If checked, the price of the selected option is added to the price of a configurable product.

Float field
    Decimal places, Min, Max, Step
        The number of decimal places and the range and step of the values customers can enter.

    Step type
        How the filter of the shop divides the values into ranges: ``Automatic``, ``Fixed step`` (ranges of the size
        ``Step``), or ``Manual steps`` (ranges you add one by one).

See also
=========

* :ref:`Properties in general <properties_concepts>`
* :ref:`Property Groups Management Interface <property_groups_management>`
