===========================================
How to add an own shipping price calculator
===========================================

In this how to you will learn how to add your own shipping price calculator.

Create an application
=====================

First you need to create a default Django application (or use an existing one),
where  you can put in your plugin. If you do not know how to do this, please
refer to the excellent `Django tutorial
<http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.


Implement the ``ShippingMethodPriceCalculator`` class
======================================================

The main part of the plugin consists of a class which must provide a certain
API.

Create the class
----------------

Create a class which inherits from ``lfs.plugins.ShippingMethodPriceCalculator``:


.. code-block:: python

    from lfs.plugins import ShippingMethodPriceCalculator

    class MyShippingMethodPriceCalculator(ShippingMethodPriceCalculator):
        pass

Add the ``get_price_net`` and ``get_price_gross`` methods
----------------------------------------------------------

This methods are called from LFS to display the shipping price or to calculate
the total price of the cart or order.

.. code-block:: python

    def get_price_net(self):
        # This doesn't make much sense, but the net price is always 11.0
        return 11.0

    def get_price_gross(self):
        return 11.0 * ((100 + self.shipping_method.tax.rate) / 100)

The complete plugin
===================

Following all pieces are sticked together to the complete plugin:

.. code-block:: python

    from lfs.plugins import ShippingMethodPriceCalculator

    class MyShippingMethodPriceCalculator(ShippingMethodPriceCalculator):
        def get_price_net(self):
            # This doesn't make much sense, but the net price is always 11.0
            return 11.0

        def get_price_gross(self):
            return 11.0 * ((100 + self.shipping_method.tax.rate) / 100)

Plug in your payment method
===========================

Now as the code is ready, you can easily plugin your shipping method price
calculator:

#. Add your application to the PYTHONPATH.

#. Add the class to the :ref:`LFS_SHIPPING_METHOD_PRICE_CALCULATORS
   <settings_lfs_shipping_price_calculators>` setting.

#. If your are using models (which is completely up to you), add the application
   to settings.INSTALLED_APPS and sync your database.

#. :doc:`Add a new shipping method </user/howtos/how_to_shipping_method>` and
   select your price calculator within the ``price_calculator`` field.

#. Save the shipping method.

Further hints
=============

* Within the ``ShippingMethodPriceCalculator`` the current request and the
  shipping method are available as instance variables::

    self.request
    self.shipping_method

* With the ``request`` you have access to the current cart (in case you need
  it)::

    from lfs.cart.utils import get_cart
    cart = get_cart(self.request)

* With the ``request`` you have access to the current customer (in case you need
  it)::

    from lfs.customer.utils import get_customer
    customer = get_customer(self.request)
