===============
Property Groups
===============

Overview
========

* Property groups are used to add ``properties`` to a product.
* Property groups can have an arbitrary amount of properties.
* Property groups can be assigned to an arbitrary amount of products
* When a property group is assigned to a product the product "inherits" all
  properties form it and can provide product specific values for the them.

Add a property group
====================

1. To add a property group go to Manage / Properties / Property Groups and click
   on the ``Add Property Group`` button (note: if there are no property groups at
   all yet you will be automatically redirect to the add form).
2. Enter the name of the property group and click on ``Add property group``.


Delete a property group
=======================

To remove a property group just visit the property group in question, click on
the ``Delete Property Group`` button and answer the confirmation question with
``yes``.

.. warning::

    Please note that all entered property values of this group's products will
    get lost.

Tabs
====

Data
----

Name
    The unique name of the property group. This is used to assign property
    groups to products.

Property
---------

Within this tab you can assign properties to the property group.

**Add properties**

You can just add properties which already exist. If you want to add new
properties please refert to :doc:`Properties </user/properties/properties>`.

1. Check the the checkbox beside the properties you want to add
2. Click on ``Assign properties``.

**Update properties**

1. Change the position from all properties you want.
2. Click on ``Update properties``.

Position
    The properties are ordered within the product by position. Lower numbers
    come first.

**Remove properties**

1. Check the the checkbox beside the properties you want to remove (within
   the ``Assigned properties`` section).
2. Click on ``Remove properties``

.. warning::

    Please note that all values which have been assigned for this property get
    lost.

Products
--------

* Within this tab you can assign products to the property group. All products
  will have the group's properties.
* Optionally you can filter the available products with the text (name) and 
  selectbox (categories) on top of the page.
* You can also navigate through the displayed products by clicking on the 
  ``First``, ``Previous``, ``Next``, ``Last`` links.

**Add products**

1. Select all checkbox beside the products you want to add to the property 
   group.
2. Click on ``Add to property group``

You will now see the above selected products within the ``Accessories`` 
section and removed from the ``Products`` section.

**Remove products**

1. Within the ``Assigned products`` section select all checkboxes beside the 
   products you want to remove from the ``property group``.
2. Click on ``Remove from property group``.

Product values
--------------

In this tab you can assign values for every product / property pair within this
group.

For that just enter the you want and click save values.

.. note::
    You can also enter the values within the ``Properties`` tab of the product. 
    :ref:`See here for more <product-properties-label>`.