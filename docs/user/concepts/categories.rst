.. index:: Category

.. _categories_concepts:

==========
Categories
==========

This section describes the concepts of categories.

Overview
========

Categories are used to structure the :doc:`products <products>` of the shop.

Every category can have either one or no parent category. In this way the
category tree is built, which serves as the essential navigation of the shop. If
a category has no parent category, it is considered a top level category.

Every category can have an arbitrary amount of products and/or sub categories.
What of these are displayed depends on the selected template. How these are
displayed depends on several format information of a category.

Each category can have several assigned :doc:`portlets <portlets>`. By default
the portlets are inherited from the parent category or from the shop preferences
(in case of top level categories). This can be blocked per :term:`slot`.

In addition a :doc:`static block <static_blocks>` can be assigned to a category,
which is displayed on top of the category page.

Please see the description of the :doc:`Category Management Interface </user/management/catalog/categories>`
in order to see more details of the information categories provide.

See Also
========

* :doc:`Category Management Interface </user/management/catalog/categories>`
