.. index:: Management commands

.. _management_commands:

===================
Management commands
===================

LFS provides these management commands. Run them with ``python manage.py <command>``.

Setup
=====

lfs_init
    Fills an empty database with a working shop: the shop with its preferences, a delivery time, a shipping method,
    payment methods, the pages for terms and imprint, and the country USA. Run it once after the first ``migrate``.

lfs_regenerate_thumbs
    Creates the missing thumbnails of the images of the shop, the categories and the products, for instance after
    :ref:`LFS_THUMBNAIL_SIZES <settings_miscellaneous>` has been changed.

lfs_generate_products
    Creates 20 products with generated data, for development and tests. Do not run it in a shop in production.

Cleanup
=======

These commands keep the database small. Run ``lfs_cleanup`` regularly, for instance daily with cron.

lfs_cleanup
    Runs all cleanup commands below at once.

cleanup_customers
    LFS creates a customer for every visitor who puts something into the cart. This command removes the customers
    who did not register and have neither a cart nor an order.

cleanup_addresses
    Removes addresses that belong neither to a customer nor to an order, for instance those of customers removed by
    ``cleanup_customers``.

cleanup_carts
    Removes carts that have not been changed for 7 days; ``--days`` sets another number of days::

        $ python manage.py cleanup_carts --days 30
