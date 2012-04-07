.. index:: Property

.. _properties_concepts:

==========
Properties
==========

This section describes the concepts of properties.

Overview
========

Generally, properties are used to extend products with miscellaneous data fields.
Properties are attached to products with the help of :doc:`property groups
</user/management/properties/property_groups>`.

In particular properties are used to create :doc:`products with variants
</user/howtos/how_to_variants>`, :doc:`configurable products
</user/howtos/how_to_configurable_product>` and :doc:`filters
</user/howtos/how_to_filters>` or just to display generic information on a product.
Additionally they can also be used to ask the shop customers to enter
information for a product which is about to be ordered.

.. _properties_concepts_types:

Types
=====

There are three types of properties.

Text Field
-----------

The property's value are plain text without any logic behind it.

Float Field
------------

The property value must be a float.

Step Type
*********

The step type is used for :ref:`filtering <portlets_concepts_filter>`. It can
be chose from three different methods how the steps are created.

Automatic
    The filter steps are calculate automatically. The base are the entered
    values of all products of a category for this property.

Fixed steps
    On base of the entered number LFS builds automatically all steps from the
    minimal to the maximum value of all entered values on the products of a
    category for this property.

Manual steps
    All steps, which are supposed to be displayed are entered manually.

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
*******

* Min: 1
* Max: 3
* Steps: 0.5

Valid values which a shop customer could input into this field are: 1, 1.5, 2,
2.5 and 3.

Select Field
------------

The property is displayed as a select box.

Select Field Properties
***********************

Display Price
    If this is checked the price of the options is displayed beside the name
    within the select box.

Add Price
    The price of the selected option of the property is added to the total
    price of a :doc:`Configurable Product
    </user/howtos/how_to_configurable_product>`.

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
