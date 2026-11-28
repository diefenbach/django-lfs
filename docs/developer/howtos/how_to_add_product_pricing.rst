.. index:: Price Calculator

========================================
How to add custom product pricing module
========================================

In this how-to you write your own price calculator: logged-in customers pay 10 % less.

A price calculator decides how LFS calculates the price of a product from the price entered in the management
interface. LFS ships with ``Price includes tax`` (``lfs.gross_price.calculator.GrossPriceCalculator``) and ``Price
excludes tax`` (``lfs.net_price.calculator.NetPriceCalculator``); both inherit from ``lfs.plugins.PriceCalculator``.

Write the calculator
====================

Put the class into an app of your project, e.g. ``myshop/pricing.py``. The simplest way is to inherit from one of
LFS's calculators and change only what differs. Here the entered price includes tax, so it inherits from the gross
price calculator and changes ``get_price``, the price before taxes are calculated:

.. code-block:: python

    from lfs.gross_price.calculator import GrossPriceCalculator


    class MemberPriceCalculator(GrossPriceCalculator):
        """Gross prices, with 10 % off for logged-in customers."""

        def get_price(self, with_properties=True, amount=1):
            price = super().get_price(with_properties, amount)
            # The request is None when LFS calculates prices outside a request, e.g. when it saves a product.
            user = getattr(self.request, "user", None)
            if user is not None and user.is_authenticated:
                price = price * 0.9
            return price

Within the calculator ``self.product`` is the product and ``self.request`` the current request (or ``None``). A
calculator that inherits from ``lfs.plugins.PriceCalculator`` directly must implement ``get_price_net``,
``get_price_gross``, the standard and for-sale variants of both, and ``price_includes_tax``; see the two calculators
of LFS.

Plug it in
==========

#. Add the app to ``INSTALLED_APPS`` (only needed if it has models or templates).

#. Offer the calculator in your settings, together with those of LFS you keep:

   .. code-block:: python

       LFS_PRICE_CALCULATORS = [
           ["lfs.gross_price.calculator.GrossPriceCalculator", _("Price includes tax")],
           ["lfs.net_price.calculator.NetPriceCalculator", _("Price excludes tax")],
           ["myshop.pricing.MemberPriceCalculator", _("Member prices")],
       ]

#. Select it for a product (``Data`` tab, ``Price calculator``) or as the default of the shop (``Shop /
   Preferences``, ``Default Values``, ``Price calculator``). Products without their own calculator use the default.

A product of 34.90 now costs 34.90 for visitors and 31.41 for logged-in customers.
