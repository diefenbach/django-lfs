======
Export
======

Overview
========

Within this tab you can define exports of products. 

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
    *default*. Developers can add more scripts.
    
Variants
    This defines how a product witth variants is exported. ``Default``: the 
    default variant will be exported. ``Cheapest``: the cheapest variant will 
    be exported. ``All``: all variants will be exported.
    
Position
    The position of the selectio within the management interface.

Product selection
-----------------

To select products just check the checkbox beside the products you want to 
export. You can also check whole categories. For every category you can 
select which variants of a product with variants will be exported (see above).

Actions
=======

Add a selection
---------------

To add a selection click on the ``Add`` button, fill in the form and click on 
``Save`` button.

Remove a selection
------------------

To remove a selection select the selection, click on the ``Delete`` button and 
answer the confirmation question with ``yes``.

Export a selection 
------------------

To export a selection select the selection and click on ``Export`` button. 
You can also call the export URL directly, e.g.: http://localhost:8000/manage/export-export/default.