.. index:: Bulk prices

=============================
Bulk prices (lfs-bulk-prices)
=============================

Prices by quantity, e.g. "from 10 pieces 8.50 each". The product page shows the tiers and updates the price when the
customer changes the amount.

Installation
============

.. code-block:: python

    INSTALLED_APPS = [..., "lfs_bulk_prices"]

    LFS_PRICE_CALCULATORS = [
        ["lfs.gross_price.calculator.GrossPriceCalculator", _("Price includes tax")],
        ["lfs.net_price.calculator.NetPriceCalculator", _("Price excludes tax")],
        ["lfs_bulk_prices.calculator.BulkPricesCalculator", _("Bulk prices")],
    ]

    # urls.py
    path("bulk-prices/", include("lfs_bulk_prices.urls")),

Then run ``python manage.py migrate``.

Usage
=====

#. On the ``Data`` tab of a product select the ``Price calculator`` ``Bulk prices`` and save. The product gets the
   tab ``Bulk prices``.

#. On that tab click ``Add Price Tier`` for every tier and enter its ``Minimum Quantity`` and ``Price per Unit``,
   then save. The first tier is the ``Base Price``. ``Percentual`` shows a tier's price in percent of the base
   price; entering a percentage calculates the price instead.

.. image:: /images/addon_bulk_prices.png
   :alt: The Bulk prices tab of a product with three price tiers

.. warning::

    Give the base price the minimum quantity 1. The calculator takes the tier with the highest minimum quantity that
    the ordered amount reaches; below the first tier the price is 0.

For a product with variants the tiers of the product apply to every variant that has no tiers of its own.
