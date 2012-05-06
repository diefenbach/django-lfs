=======================
How to add own criteria
=======================

In this how-to you will learn how to add own criteria to LFS.

The goal in this how-to is to create a criterion, for which the :term:`shop
manager` can enter a SKU and decide (via operators) whether the criterion is
valid if the product with the entered SKU is within the cart or not.

You can :download:`download the example application
<product_criterion.tar.gz>` here.

Create an application
=====================

First you need to create a default :term:`Django` application (or use an
existing one), where  you can put in your plugin. If you do not know how to do
this, please refer to the excellent `Django tutorial
<http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

Implement the Criterion Model
=============================

The main part of the application consists of a criterion model which must
inherit from the ``Criterion`` base class.

Create the Class
----------------

.. code-block:: python

    class ProductCriterion(Criterion):
        value = models.CharField(max_length=100)

The only attribute we need is the value the :term:`shop manager` will save for
the criterion. The attribute can have any type you need. In this example we use
a simple character field. The entered SKU is checked within the products in the
cart. Dependent on the chosen operator the criteria is valid if the product is
within the cart or not.

Implement necessary Methods
---------------------------

In the next steps we implement all necessary methods which are needed to make
the criterion work. In this case these are ``get_operators`` and ``is_valid``.

The ``get_operators`` method needs to return the available operators for this
criterion. It is a list of list, whereas the first value is an integer and the
second value is the name of the operator.

.. code-block:: python

    def get_operators(self):
        return [
            [0, _(u"Is in cart")],
            [1, _(u"Is not in cart")],
        ]

The ``is_valid`` method needs to return a boolean. If it returns ``True`` the
criterion is considered valid, it returns ``False`` the criterion is considered
not valid.

.. code-block:: python

    def is_valid(self):
        if self.product:
            return self.value == self.product.sku
        elif self.cart:
            result = any([self.value == item.product.sku for item in self.cart.get_items()])
            return result if self.operator == 0 else not result
        else:
            return False

.. note::

    Within the ``is_valid`` method (as in all methods of the ``Criterion``
    class) following attributes are available:

        product
            This is only set, when the criterion is called from the product
            detail view otherwise it is ``None``.

        cart
            The current cart of the current user.

        request
            The current request.

Plug in the Criterion
=====================

Now as the code is ready, you can easily plugin your own criterion:

#. Add your application to the PYTHONPATH

#. Add your application to settings.INSTALLED_APPS and sync your database::

     INSTALLED_APPS = (
          ...
          "product_criterion",
     )

#. Add the class to the :ref:`LFS_CRITERIA <settings_lfs_criteria>` setting::

     LFS_CRITERIA = [
         ...
         ["product_criterion.models.ProductCriterion", _(u"Product Criterion")],
     ]

#. As all criteria are models, you have to synchronize your database::

     $ bin/django syncdb

#. Restart your instance and the criterion should be available for selection,
   for instance within the discount criteria tab.

And that's it
=============

You should now see your criterion within the criteria tab of ``Discounts`` for
instance. You can enter a product SKU to it and select one of the above
mentioned operators.

Good to know
============

* You can also create criteria with select or multiple select fields. See the
  :ref:`API <api_criterion>` or the default ``Country`` criterion within
  ``lfs.criteria.models`` for more.

* You can override more than the two mentioned methods above. See the
  :ref:`Criterion API <api_criterion>` which methods are provided by the base
  class.

See Also
========

* :doc:`Criteria concept </user/concepts/criteria>`
* :ref:`Criterion API <api_criterion>`
* Look into the default criteria within ``lfs.criteria.models`` to see how these
  are implemented
