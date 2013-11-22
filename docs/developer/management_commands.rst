.. index:: Management commands

.. management_commands:

===================
Management commands
===================

LFS provides few management methods that should be used to keep your LFS instance clean. These are:

LFS Cleanup
===========

Calls all LFS cleanup commands at once. Detailed definition of other cleanup commands can be found below.

    $ bin/django lfs_cleanup


Cleanup customers
=================

LFS creates Customer object for each customer that adds something to the cart. Sometimes these customers do not proceed
to the checkout so these Customer objects become useless. This command removes unnecessary customer objects from database.
You can run in with cron.daily.

    $ bin/django cleanup_customers


Cleanup addresses
=================

LFS creates Address objects in a number of places. These are bound to the customer or to the order. Sometimes it is
possible that Address objects become orphans (eg. when Customer object is removed by not using cleanup_customers command).
This command removes unnecessary address objects.

    $ bin/django cleanup_addresses


Cleanup carts
=================

LFS creates Cart objects when customers need to add something to the cart. These objects become unnecessary at some
point and it makes no sense to hold them forever. This command removes old carts

    $ bin/django cleanup_carts
