=================================
How to Add a Configurable Product
=================================

In this how-to you will learn how to add a configurable product.

Add Properties
==============

A configurable product is based on :doc:`properties
</user/concepts/properties>`. So we need to enter them at first.

* Go to the management interface.

* Go to the ``Properties / Properties`` menu.

* Click on the ``Add Property`` site action and enter the name of the property,
  for instance "Hard drive". Then click on the ``Add Property`` button.

* Now check ``Configurable`` within the data form of the property and click on
  ``Save Property``.

* Change the ``Field Type`` to ``Select Field`` and click on ``Save Property
  Type``.

* Now add the options, for instance:

  * Name 100GB / Price: 100
  * Name 200GB / Price: 200
  * Name 400GB / Price: 400

* Repeat the steps 3-7 for a property called "RAM".

* Go to Properties / Property Groups

* Click on the ``Add Property Group`` site action and enter the name of the
  property group, for instance "PC". Then click the ``Add Property Group``
  button.

* Go to the ``Properties`` tab, select the properties "Hard drive" and "RAM"
  and click on ``Assign Properties``.

Add the Product
===============

* Go to the management interface.

* Go to ``Catalog / Products`` menu.

* Click on ``Add product`` in order to add new product.

* Enter the name and the slug and click on ``Add product``.

* Now you can enter further data as you would do for standard products.

* Change the product type from ``Standard`` to ``Configurable``
  and click ``Change``.

* Go to the ``Properties`` tab.

* Select the ``PC`` property group and click on ``Update Property Group``.

* Select the default values of the properties and click on ``Update Default
  Values``.

That's it
=========
You have successfully completed this tutorial!

Now click on ``Goto Product`` and you will see that the product has two select
boxes from which the customer can select the options you provide above. The
prices are automatically updated when the options are changed.

See Also
========

* :ref:`Product Concepts <products_concepts_configurable_product>`
* :doc:`Property Concepts </user/concepts/properties>`

