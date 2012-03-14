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

0.7.0 beta 3
------------

* Using django-portal 0.9
* Bugfix: don't display non-active products within cart nor add them to order with checkout; Adapt tests; fixed issue #154.
* Bugfix: don't delete OrderItems when a product is deleted.
* Bugfix: added default values for LFS_SHIPPING_* settings.
* Bugfix: removed redundant javascript code; issue #153
* Improved: added link to product within order detail view in LM; issue #149
* Improved: cleaned up displaying of addresses of orders within LM.
* Updated: Czech translation (naro)
* Updated: German translation (naro)

0.7.0 beta 2
------------

* Security fix
* Added manufacturer field to product management (Maciej Wiśniowski)
* Bugfix: fixed pagination for product page; issue #152 (Maciej Wiśniowski)
* Bugfix: fixed deleting of image for payment and shipping methods; issue #150
* Bugfix: fixed markup; #issue #148
* Bugfix: fixed updating of attachments; issue #147
* Improved javascript: prevent FOUC for category-tabs and manage-tabs;

0.7.0 beta 1
------------

* Added customer related taxes
* Added global image management
* Added django_compressor
* Added pluggable shipping price calculators
* Added pluggable order number generation
* Added calculation of base price
* Added product attachments
* Added more portlets: featured products, for sale products
* Aded SEO information for shop and pages
* Added portlets for pages
* Added type of quantity field
* Added context aware help for the management interface
* Improved pluggable product price calculators
* Improved pluggable payment processors
* Improved mails templates

HISTORY
=======

For the complete history please look into HISTORY.txt
