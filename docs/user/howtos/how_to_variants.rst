==================================
How To Add a Product with Variants
==================================

Overview
========

In this how-to you will learn how to add a product with variants.

.. include:: /includes/demo_shop.rst

Steps
=====

1. Go to the LFS Management Interface.

2. Go to ``Catalog / Products``.

3. Click on ``Add Product`` in order to add new product.

4. Enter the ``Name``, and the ``Slug`` of the product and click on ``Add
   product``.

5. Now you can enter further data as you would do for standard products for
   instance the price. Please note that this are in case of a ``Product with
   Variants`` just default values, which can be overwritten for every single
   variant later.

6. Change the product's type from ``Standard`` to ``Product with Variants``
   and click ``change``. You will notice that there is now a ``Variants`` tab.

7. Go to the ``Variants`` tab.

8. Click on the pencil left beside the ``Local Properties`` title in order to
   display the local properties add form.

9. Enter ``Color`` in the text field and click on ``Add Property``.

   .. note::

     You can also use :doc:`global properties </user/concepts/properties>` to
     create variants, but this is beyond of these how-to.

10. Enter ``Red`` into the now provided option field and click on ``Add Option``.

11. Repeat step 10 with ``Green`` and ``Blue``.

    .. note::

      For convenience you can also add ``Red, Green, Blue`` to add all options
      at once.

12. Now go to the ``Variants`` section and select ``All`` below ``Color``
    option. Click on ``Add Variants(s)``. This will create all variants based
    on the option you have entered above.

13. Click on the pencil of a variant in order to open its edit form.

14. By default the data is inherited from the parent. In order to override a
    field activate it - check the check box beside the field - and enter some
    information to it for instance for the price of a variant.

15. Repeat that for every variant you want to change.

16. Click on the ``Base Article`` site action in order to go back to the parent
    product.

17. Go to the ``Variants`` tab. You should be there automatically.

18. Check the ``Active`` check box. This will check the active check boxes of
    all variants and click on the ``Save`` button.

19. Select the default variant by checking one of the radio boxes below the
    ``Default`` title. This variant is displayed if the shop customer visits the
    ``Product with Variant``.

20. Go to the ``Product`` tab.

21. Check the ``Active`` check box. This will activate the whole ``Product with
    Variants``.

That's it
=========

Now click on ``Goto Product`` and you will see your newly created ``Product with
variants``. There is a ``Variants`` section from which the customer can select
the variants the product provides. All information of the product (which has been
overwritten by a variant) are automatically updated if the customer choose a
variant.

What's next
===========

* Add more properties and options in order to create more complex variants.
* Use :doc:`global properties </user/concepts/properties>` in order to create
  variants.
* Check the difference between the both display types list and select.

See also
========

* :doc:`Products Concept </user/concepts/products>`
* :doc:`Properties Concept </user/concepts/properties>`
