.. index:: Property

==========
Properties
==========

* Properties can be added to products via property groups.
* Properties are an flexible way to add flexible properties to Products.
* Properties are used to create :ref:`variants <product-product-with-variant-label>`
* Properties are used to create :ref:`configurable products <product-configurable-product-label>`
* Properties can be used to filter products

Tabs
====

Data
----

Position
    The position within the product.

Name
    The uniqe name of the property. This is displayed within the management
    interface to select the property for several purposes.

Title
    The title of the property. This is displayed to the shop cusotmer.

Filterable
    If this is checked the property will be displayed for filtering (within
    the filter :term:`portlet`).

Display no results
    If this is checked filter ranges with no products will be displayed within
    the filter portlet. Otherwise they will be removed.

Display on product
    If this is checked the property will be displayed on the product. This is
    only displayed if filterable is checked.

Configurable
    If this is checked the property will be displayed for selection/input on
    a configurable product

Required
    If this is checked the property must be selected/entered on a configurable
    product. This is only displayed if configurable is checked.

Unit
    The unit of the property, e.g. meter, liter or whatever you want. This is
    just a simple string without logic.

Field type
    The type of the field.

    Select the type you want and click ``Save property type``. Depended on
    the field type you have selected you need to enter additionally
    information.

    Text field
        The property's value are plain text without any logic behind it. You
        don't have to enter additionally information.

    Float field
        The property value must be float:

            **Step type**

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

            **Validators**

            Validators are used within configurable products.

            Decimal places
                The amount of decimal places which will displayed to the
                customer.

            Min
                The minimum value of the field.

            Max
                The maximum value of the field.

            Step
                The valid steps from minimum to maximum value

            **Example**:

            * Min: 1
            * Max: 3
            * Steps: 0.5

            Valid values are: 1, 1.5, 2, 2.5 and 3

    Select field

        The value of the property can be selected from several options.
    
        **Select field properties**
        
        Display price
            The price of the option is displayed
        
        Add price
            The price of the selected property is added to the total price
            of a configurable product.

        **Select field options**

        You need to enter every single options for this property. For that
        please enter:

        * position
        * name
        * price (optional)

        The options are ordered by position, lower numbers first. The names
        are displayed within several selection fields. The price is used
        to calculate the total price of a configurable product (if add price
        is selected).
