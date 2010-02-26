==========
Properties
==========

* Properties can be added to products via property groups.
* Properties are an flexible way to add flexible properties to Products.
* Properties are used to create :ref:`variants <product-product-with-variant-label>`
* Properties can be used to filter products

Tabs
====

Data
----

Name
    The name of the property. This is displayed within the product, the filter of
    the select boxes to create/select variants.

Filterable
    If this is checked the property will be displayed for filtering (within
    the filter :term:`portlet`).

Unit
    The unit of the property, e.g. meter, liter or whatever you want. This is
    just a simple string wihthout logic.

Position
    The position within the management interface (deprecated)

Display on product
    If this is checked the property will be displayed on the product.

Display no results
    If this is checked filter ranges with no products will be displayed within 
    the filter portlet. Otherwise they will be removed.

Field type
    The type of the field.

    Select the type you want and click ``Save property type``. Dependend on
    the field type you have selected you need to enter additionally
    information.

    Text field
        The property's value are plain text without any logic behind it. You
        don't have to enter additionally information.

    Number field
        The property's values must be number. You need to choose a ``Step
        type``:

            Automatic
                The filter steps are calculate automatically. LFS tries to
                calculate decent steps based on the existing values.

            Fixed step
                You need to enter a fixed step for the filter, e.g. 5. LFS will
                the generate the filter from the min to the max field with the
                provided step. Just enter a number into the provided text field
                and click on ``Save step``. You can change the step any time.

            Manual steps
                You need to enter every step. LFS will just display the steps
                you provide. Enter a step to the provided text field and
                click on ``Add step``. To remove a step click on the red
                'X' beside the step.

    Select field
        The value of the propery can be selected from several options. 
        
        You need to enter every single options for this property. For that 
        enter a position and a name. The options are ordered by position, 
        lower numbers first. The names are displayed as filter options within 
        the filter portlet.
