=================================
How To Add a Configurable Product
=================================

Overview
========

In this how-to you will learn how to add a configurable product.

.. include:: /includes/demo_shop.rst

Steps
=====

Add Properties
--------------

A configurable product is based on :doc:`properties
</user/concepts/properties>`. So we need to enter them at first.

1. Go to the management interface.

2. Go to the ``Properties / Properties`` menu.

3. Click on the ``Add Property`` site action and enter the name of the property,
   for instance "Hard drive". Then click on the ``Add Property`` button.

4. Now check ``Configurable`` within the data form of the property and click on
   ``Save Property``.

5. Change the ``Field Type`` to ``Select Field`` and click on ``Save Property
   Type``.

6. Now add the options, for instance:

  * Name: 250GB / Price:  50.0
  * Name: 500GB / Price: 100.0
  * Name: 750GB / Price: 150.0

7. Go to Properties / Property Groups

8. Click on the ``Add Property Group`` site action and enter the name of the
   property group, for instance "PC". Then click the ``Add Property Group``
   button.

9. Go to the ``Properties`` tab, select the properties "Hard drive" and "RAM"
   and click on ``Assign Properties``.

Add the Product
---------------

10. Go to the management interface.

11. Go to ``Catalog / Products`` menu.

12. Click on ``Add product`` in order to add new product.

13. Enter the name and the slug and click on ``Add product``.

14. Enter further data as you would do for standard products, like prices,
    descriptions and so on.

15. Change the product type from ``Standard`` to ``Configurable`` and click
    ``Change``.

16. Go to the ``Properties`` tab.

17. Select the ``PC`` property group and click on ``Update Property Group``.

18. Select the default values of the properties and click on ``Update Default
    Values``. The default values will be selected when a customer views the
    product.

That's it
=========

Now click on ``Goto Product`` and you will see that the product has a select box
from which the customer can select the options you provide above. The prices are
automatically updated when the options are changed. If the customer adds the
product to the cart, the selected option is stored on the product.

What's next
===========

* Add more properties and options (see steps 3-7 on the ``Add Properties``
  section above).

* Add a float field to the configurable product and see how the customer can be
  asked to enter a decimal number.

* Add a text field to the configurable product and see how the customer can be
  asked to enter a text.

See Also
========

* :ref:`Product Concepts <products_concepts_configurable_product>`
* :doc:`Property Concepts </user/concepts/properties>`
