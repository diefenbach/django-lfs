=================================
How To Add a Product with Filters
=================================

Overview
========

In this how-to you will learn how to create a product with filters. At the end
of it you will have added a property group a property, a category with three
products and a filter portlet.

.. include:: /includes/demo_shop.rst

Steps
=====

First we will add the corresponding filter portlet:

1. Go to Management / Shop / Preferences.

.. image:: /images/how_to_filters_1.*

2. Go to the "Portlets" tab.
3. Select ``Filter`` portlet and click ``Add portlet``. Enter *Filter* in the
   ``Title`` field and click ``Save portlet``. You should now see the filter
   portlet within the ``Left slot`` section.

.. image:: /images/how_to_filters_2.*

Now we will add properties, which are the base for the product filters.

4. Go to Management / Properties / Properties.
5. Add a new property by clicking ``Add property``. (If there is no  property.
   at all yet you will see the *Add property form* automatically).
6. Enter the ``Name`` of the property, in our case *Size* and click
   ``Add property``.
7. Go to ``Field type``, select ``Select field`` and click ``Save property
   type``.
8. Now go to ``Options`` and fill in the ``Name`` field. In our case *Small*.
   Click ``Add option``.
9. Repeat step 8 for *Middle* and *Large*. Now you should see three options
   within property *Size*: *Small*, *Middle* and *Large*.

.. image:: /images/how_to_filters_3.*

Now we will add a property group.

.. note::

    Every property has to belong exactly to one property group in order to
    use it with a product.

10. Got to Management / Properties / Property Groups.
11. Add a new property group by clicking the ``Add property group`` button.
    (If there is no property group at all yet you will see the *Add property
    group* form automatically).
12. Enter the ``Name`` of the property, in our case *T-Shirts* and click
    ``Add property group``.

Now assign the property to the property group:

13. Go to the "Properties" tab.
14. Select *Size* and click ``Assign properties``.


You should now see *Size* within ``Assigned properties``.

.. image:: /images/how_to_filters_4.*

We will now add the ``Property group`` to some products.

15. Go to Management / Catalog / Products.
16. Add a new product clicking ``Add product``. (If there is no product at all
    yet you will see the *Add product" form* automatically).
17. Fill in ``Name`` *T-Shirt One* and ``Price`` *10.00* and click ``Add product``.

No we assign values to the properties:

18. Go to the ``Properties`` tab of that product.
19. Select our ``Property group`` *T-Shirts* and click ``Update property groups``
    You will now see the ``Property`` *Size*.
20. Select ``Size`` *Small*.
21. Repeat Steps 16 - 20 for *T-Shirt Two* and *T-Shirt Three* and assign
    sizes *Middle* and *Large* and prices *100.00* and *1000.00*. Now you should
    have three products *T-Shirt One*, *T-Shirt Two* and *T-Shirt Three* with
    sizes *Small*, *Middle* and *Large* and prices *10.00*, *100.00* and
    *1000.00*.

We need to make the products active:

22. Go to Management / Catalog / Products Overview.
23. Select ``Active`` for all products and click ``Save``.

.. image:: /images/how_to_filters_5.*

Now we add a new category *T-Shirts*:

.. note::

    Filtering takes place on products of a category, hence we add a category
    for our newly products.

24. Go to Management / Catalog / Categories.
25. Add a new category by clicking "Add category". (If there is no category at
    all  yet you will see the "Add category" form automatically).
26. Fill in the ``Name``: *T-Shirts* and click ``Add category``.

Now we assign the products to the category:

27. Go to the products tab of that category.
28. Select the products *T-Shirt One*, *T-Shirt Two*, *T-Shirt Three* and
    click ``Add to category``.

Now we are ready to preview our new content:

29. Click on the ``Preview`` button. You should now see the filter portlet
    with the ability to select the sizes *Small*, *Middle* and *Large* and prices *0 - 500.00* and *501.00 - 1000.00*.

.. image:: /images/how_to_filters_6.*

What's next?
============

* Add some more properties to the property group *T-Shirts*.

* Add the property group *T-Shirts* to more products.

* Assign products and values via *Property Groups*:

  1. Go to Properties / Properties Groups

  2. Select *T-Shirts*

  3. Go to *Products* tab

  4. Go to *Values* tab

* Check out the other options of the properties, e.g. the ``Field type`` or the
  ``Unit`` field.

* Check out creating variants on base of properties and see how filters work
  with variants too.
