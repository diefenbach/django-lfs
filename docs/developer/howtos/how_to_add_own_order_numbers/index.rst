=========================================
How to add an own order numbers generator
=========================================

Overview
========

LFS order numbers generator is pluggable. In this tutorial you will learn how to
add an own one.

Please see also the :download:`complete example application
<country_specific_order_numbers.tar.gz>` or refer to the default implementation
of LFS within ``lfs_order_numbers``.

Create an application
=====================

First you need to create a default Django application (or use an existing one).
If you do not know how to do this, please refer to the excellent `Django
tutorial <http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

The structure of the application should look at least like this::

    my_order_numbers
        __init__.py
        models.py


Implement the application
=========================

Add the model
-------------

Within ``models.py`` file of your application create a class called
``OrderNumberGenerator`` which inherits from LFS' OrderNumberGenerator base
class and add a method to it called ``get_next``:

.. code-block:: python

    from lfs.plugins import OrderNumberGenerator as Base

    class OrderNumberGenerator(Base):
        def get_next(self, formatted=True):
            return "DOE-4711"

The ``get_next`` method is called when the shop customer submits a new order. It
**must** return a character value which will become the order number of the new
order.

Plug in your order number generator
===================================

Now as the code is ready, you can easily plugin your payment method:

#. Add your application to the PYTHONPATH.

#. Add your class to ``settings.py``

    LFS_ORDER_NUMBER_GENERATOR = "my_order_numbers.models.OrderNumberGenerator"

#. Add your application to settings.INSTALLED_APPS and sync the database.

And that's it
=============

You should now see your form within the ``Order Numbers`` tab within
``Shop/Preference`` and the ``get_next`` method of your model should be
called to generate a new order number.

Optionally Add your own Template
================================

Optionally you can add your own HTML for the management interface. For this
just add the order_numbers_tab.html template to your application::

    my_order_numbers
        templates
            manage
                order_numbers
                    order_numbers_tab.html

Please refer to the standard template of LFS to get more details. You can find
this on following place:

    ``lfs/templates/manage/order_numbers/order_numbers_tab.html``

In this case  please make sure that your ``my_order_numbers`` application
stands **before** ``lfs`` within ``INSTALLED_APPS`` of ``settings.py`` so
that LFS' default ``order_numbers_tab.html`` template is overwritten.

Further hints
=============

* The form is automatically created from the model you provide. However you can
  provide a own own by overwriting the ``get_form`` method. :ref:`See the API
  for more <order_number_generator>`.

* If you just want to exclude certain fields from the automatically generated
  form you can overwrite the ``exclude_form_fields``. The return value is just
  passed to the exclude attribute of the from Meta class. :ref:`See the API for
  more <order_number_generator>`.

Available information
=====================

Within the ``get_next`` method of your new class you have access to following
information:

self.request
    The current request

self.user
    The current user

self.customer
    The current customer

self.cart
    The current cart

self.order
    The order which is about to be created.

Please note that you have also access to the products of the order via the
``items`` attribute. For instance:

.. code-block:: python

    for item in self.order.items.all():
        product = item.product

See the also the ``Order`` and ``OrderItem`` classes for more information.
