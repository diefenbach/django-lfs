How to add custom product pricing module
========================================

In this tutorial you will learn how to your own custom product pricing module.

Create an application
----------------------

First you need to create a default Django application (or use an existing one).

If you do not know how to do this, please refer to the excellent
`Django tutorial <http://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

Implement the PriceCalculator class
--------------------------------------

Within ``__init__.py`` file of your application (or anywhere you choose) create a class that inherits from
lfs.price.PricingCalculator and implement all inherited methods.

.. code-block:: python

    from lfs.price import PriceCalculator

    class CustomPriceCalculator(PriceCalculator):

        def get_price(self, with_properties=True):
            return self.get_price_net()

        ... Other Methods...


Plug in the custom price calculator
-----------------------------------

* Add your application to the PYTHONPATH.
* Add the application to settings.INSTALLED_APPS.
* If your are using models (which is completely up to you), sync your database.

**Add your custom price calculator to lfs.core.settings.LFS_PRICE_CALCULATOR_CHOICES**

Edit the choices tuple lfs.core.settings.LFS_PRICE_CALCULATOR_CHOICES to make your custom pricing calculator available
to products in the manage interface

.. code-block:: python

    LFS_PRICE_CALCULATOR_CHOICES = [('lfs.gross_price.GrossPriceCalculator', 'Price including tax'),
                                ('lfs.net_price.NetPriceCalculator', 'Price excluding tax'),
                                ('mycustom_price.CustomPriceCalculator', 'My Pricing Calculator'),
                               ]

You can optionally set the default pricing calculator to your own module e.g.

.. code-block:: python

    LFS_DEFAULT_PRICE_CALCULATOR="mycustom_price.CustomPriceCalculator'"

**Set product pricing calculator in manage inteface**

* Browse to http://yourshopdomain/manage and login.
* Select Catalog - Product
* Select the product whose price calculator you wish to change.
* Select the pricing calculator tab
* Select your new pricing calculator from the drop down menu of choices.
* Save the product.
* Browse to your product in your shop and you should see the new price as calculated by your custom pricing calculator.