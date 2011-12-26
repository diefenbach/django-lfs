.. index:: Property

.. _properties_concepts:

==========
Properties
==========

This section describes the concepts of properties.

Concept
=======

Properties are used to add flexible attributes on a product, like color, size,
material, etc. They organized with :doc:`property groups
</user/management/properties/property_groups>`, which are assigned to products.

Properties can be used to create product filters, variants and configurable
products or just to display information on a product. They can also be used to
ask the shop customers to enter information for to product which should be ordered
in other words for every property which is assigned to a product users (shop
owners or show customers) can enter information.

.. _properties_concepts_types:

Property Types
==============

There are three types of properties.

Text Field
-----------

The property's value are plain text without any logic behind it.

Float Field
------------

The property value must be a float.

Additional Data
^^^^^^^^^^^^^^^

Step Type
*********

The step type is used for :ref:`filtering <portlets_concepts_filter>`. You
can choose from three different methods how the steps are created.

Automatic
    The filter steps are calculate automatically. LFS tries to
    calculate decent steps based on the existing values.

Fixed step
    You need to enter a fixed step for the filter, e.g. 5. LFS will
    then generate the filter from the min to the max field with the
    provided step.

Manual steps
    You need to enter every step. LFS will just display the steps
    you provide.

Validators
**********

Validators are used to validate customer inputs into property fields.

Decimal places
    The amount of decimal places which are allowed.

Min
    The minimum value of the field.

Max
    The maximum value of the field.

Step
    The valid steps from minimum to maximum value.

Example
^^^^^^^

* Min: 1
* Max: 3
* Steps: 0.5

Valid values which a shop customer could input into this field would be:
1, 1.5, 2, 2.5 and 3.

Select Field
------------

The property is displayed as a select box.

Additional Data
^^^^^^^^^^^^^^^

Select Field Properties
***********************

Display Price
    If this is checked the price of the options is displayed beside the name
    within the select box.

Add Price
    The price of the selected option of the property is added to the total
    price of a ``Configurable Product``.

Select Field Options
********************

Every single option for a ``Select Field Property`` has to be entered. These
have following information:

* Position
* Name
* Price (optional)

The options are ordered by position, lower numbers are displayed first. The
names are displayed within several selection fields. if ``Add Price`` is selected,
the price is used to calculate the total price of a :ref:`Configurable Product
<products_concepts_configurable_product>`.

See Also
========

* :doc:`Properties Management Interface </user/management/properties/properties>`
* :ref:`Properties within the Product Management Interface <products_management_properties>`
* :doc:`/user/howtos/how_to_filters`
* :doc:`/user/howtos/how_to_variants`
* :doc:`Local properties </user/concepts/local_properties>`
