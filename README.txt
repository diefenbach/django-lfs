What is it?
===========

LFS is an online shop based on Python, Django and jQuery.

Information
===========

For more information please visit:

* http://www.getlfs.com

Documentation
=============

For the latest documentation please visit:

* http://docs.getlfs.com

Demo shop
=========

A demo shop can be tried here:

* http://demo.getlfs.com

The latest development state can be found here:

* http://dev.getlfs.com

Changes
=======

0.6.5 (2012-02-03)
------------------

* Bugfix: added csrftoken for rating mails (Maciej Wiśniowski)
* Bugfix: fixed ImageWithThumbsField (Maciej Wiśniowski)
* Updated romanian translations (olimpiu)
* Updated polish translations (Maciej Wiśniowski)

0.6.4 (2012-01-08)
------------------

* Bugfix: fixed price calculation of configurable products.

0.6.3 (2011-12-31)
------------------

* Bugfix: fixed update of prices if a configurable product is for sale.
* Bugfix: fixed calculation of property prices for configurable products.
* Bugfix: fixed saving of property data (added missing csrf token).
* Bugfix: fixed removing products / properties from a group.
* Bugfix: fixed filtering for float field steps.

0.6.2 (2011-12-24)
------------------

* Bugfix: fixed issue with utf-8 support for MySQL; issue #126
* Bugfix: fixed product filtering; issue #124

0.6.1 (2011-12-16)
------------------

* Bugfix: fixed category management; issue #123
* Bugfix: fixed adding of payment method: added csrf_token
* Bugfix: fixed german address form: removed "Area" field, made fields required
* Bugfix: fixed set/reset of product filters within management UI
* Bugfix: fixed amount of products per price filter step
* Bugfix: added translatable label for country field
* Updated italian translations (pippo64)
* Updated dutch translations (bastichelaar)

0.6.0 (2011-12-10)
-------------------

* Final release

HISTORY
=======

For the complete history please look into HISTORY.txt
