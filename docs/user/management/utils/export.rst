======
Export
======

Within this tab you can export selections of products.

Site Actions
============

Add Export
    Adds a new export.

Delete Export
    Deletes the currently displayed export.

Download Export
    Downloads the currently displayed export.

Tabs
====

Data
----

Name
    The name of the product selection. This is just for internal reasons.

Slug
    The unique part of the selection's URL. This is used to call the selection
    from outside.

Script
    The script which is used to create the export. By default there is only
    the ``Generic`` script. Developers can :ref:`add more scripts
    <developers_howto_export>`.

Variants
    This defines how a product with variants is exported by default. This is
    either the default variant, the cheapest variant or all variants.

Position
    The position of the selection within the management interface.

Products
--------

Within this tab you can select which products are supposed to be exported.

To export whole categories just select the check box beside the category you want
to  export. If you want just a sub category or single products of category,
click on the category to expand the children.

For every category you can overwrite the default settings which variant(s) of a
``product with variants`` will be exported. This is either the default variant,
the cheapest variant or all variants.

See Also
========

* :ref:`How to create a export script <developers_howto_export>`
