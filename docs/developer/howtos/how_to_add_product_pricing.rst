.. index:: Price Calculator

========================================
How to add custom product pricing module
========================================

In this tutorial you will learn how to your own custom product pricing module.

Create an application
=====================

First you need to create a default Django application (or use an existing one).
If you do not know how to do this, please refer to the excellent `Django
tutorial <http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

Implement the price calculator class
====================================

Within ``__init__.py`` file of your application (or anywhere you choose) create
a class that inherits from lfs.plugins.PricingCalculator and implement all
inherited methods.

.. code-block:: python

    from lfs.plugins import PriceCalculator

    class CustomPriceCalculator(PriceCalculator):

        def get_price(self, with_properties=True):
            return self.get_price_net()

        ... Other Methods...


Plug in the custom price calculator
===================================

1. Add your application to the PYTHONPATH.

2. Add the application to settings.INSTALLED_APPS.

3. If your are using models (which is completely up to you), sync your database.

4. Edit the dictionary lfs.core.settings.LFS_PRICE_CALCULATORS to make
   your custom pricing calculator available to products in the manage interface

.. code-block:: python

    LFS_PRICE_CALCULATORS = [
        ["lfs.gross_price.calculator.GrossPriceCalculator", _(u"Price includes tax")],
        ["lfs.net_price.calculator.NetPriceCalculator", _(u"Price excludes tax")],
        ["mycustom_price.CustomPriceCalculator", _(u"My Pricing Calculator")],
    ]

Set the shop default price calculator
=====================================

1. Go to the LFS Management Interface.

2. Select ``Shop / Preferences``.

3. Select ``Default Values`` and go the ``Price Calculator`` section.

4. Select your new pricing calculator from the drop down menu of choices.

5. Save the default values.

.. note::

    All products with an unset price calculator will default to using the shop
    price calculator.

Set the product pricing calculator
==================================

1. Browse to http://yourshopdomain/manage and login.

2. Select ``Catalog / Product``.

3. Select the product whose price calculator you wish to change.

4. Select the ``Data Tab`` and scroll to the ``Prices`` section.

5. Select your new pricing calculator from the drop down menu.

6. Click on ``Save Data``.

7. Now browse to the customer view of the product and you should see the price
   as calculated by your custom pricing calculator.
