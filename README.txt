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

Changes
=======

0.7.7 (2013-01-20)
------------------

* Update: updated Czech translation (Radim Novotny).
* Update: updated Mexican translations (tzicatl).
* Improvement: Don't use more than one h1 tag on the product page but use h1 and h2 (Radim Novotny).
* Improvement: Show search query in the input box if there is any query. Also added pagination to the bottom of search results page (Radim Novotny).
* Bugfix: fixed calculation of discount net price within order; issue #36
* Bugfix: fixed display of amount for discounts within management.
* Bugfix: fixed sorting handling for SOLR (Radim Novotny)
* Bugfix: fixed display of properties for locale.
* Bugfix: fixed calculation of 'calculated price' for different locales.
* Bugfix: fixed calculation and display of packings.
* Bugfix: fixed display of variant property values within products management.

0.7.6 (2012-06-24)
------------------

* Bugfix: fixed saving of property values for products with variants (introduced with 0.7.5.).

0.7.5 (2012-06-23)
------------------

* Bugfix: Don't convert images with mode RGBA to RGB. That results in loss of alpha channel. (Michael Jenny)
* Bugfix: fixed saving of property values for products with variants. (Michael Jenny)
* Bugfix: fixed calculation of discount price.
* Bugfix: fixed display of for sale price for variants within product detail view.
* Bugfix: fixed datepicker handling for stock etc. (Maciej Wiśniowski)

HISTORY
=======

For the complete history please look into HISTORY.txt
