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

Now as the code is ready, you can plug in your order number generator:

#. Add your class to ``settings.py``

    LFS_ORDER_NUMBER_GENERATOR = "my_order_numbers.models.OrderNumberGenerator"

#. Add your application to ``INSTALLED_APPS``, create its migration (``python manage.py makemigrations <app>``) and
   run ``python manage.py migrate``.

And that's it
=============

You should now see your form within the ``Order Numbers`` tab within
``Shop/Preference`` and the ``get_next`` method of your model should be
called to generate a new order number.

Optionally Add your own Template
================================

The ``Order Numbers`` tab renders the form that your model's ``get_form`` returns, with LFS's template
``manage/shop/tabs/_order_numbers.html``. To change the HTML, put a template with that path into your app and list
the app **before** the LFS apps in ``INSTALLED_APPS``, so its template wins.

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
