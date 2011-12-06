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

* http://packages.python.org/django-lfs/

Demo shop
=========

A demo shop can be tried here:

* http://demo.getlfs.com:81 (version 0.6)
* http://demo.getlfs.com (version 0.5)

Changes
=======

0.6.0 beta 7 (2011-12-06)
-------------------------

* Bugfix: fixed filtered products for variants; #issue #122
* Bugfix: fixed display of error indicator for packing_unit

0.6.0 beta 6 (2011-12-02)
-------------------------

* Bugfix: added default country to shipping countries within lfs_init.
* Bugfix: fixed validation of shipping and invoice addresses. (mickt)
* Bugfix: fixed page selection within product management interface.
* Bugfix: fixed display of selectable products within category's products tab.
* Bugfix: fixed displaying of property values within product management interface.
* Bugfix: fixed filter portlet.
* Bugfix: fixed management of country criterion.
* Changed: removed growl message from checkout view.
* Changed: removed displaying of error fields checkout view.
* Added migration of shop_countries.
* Added migration of orders.
* Updated russian translations (Belanchuk)

0.6.0 beta 5 (2011-11-28)
-------------------------

* Bugfix: fixed delete links for properties and options within product's variants tab
* Bugfix: fixed saving of variant list type.
* Bugfix: fixed my account (added missing csrf_tokens; issue #114).
* Bugfix: fixed discounts
* Added dutch translations (BasTichelaar)
* Updated romanian translations (bsdwave)

0.6.0 beta 4 (2011-11-26)
-------------------------
* Bugfix: fixed display of vouchers options tab
* Bugfix: don't translate label of supplier_id field within lfs_migrate
* Bugfix: fixed the management of a customer if he has no cart yet
* Bugfix: fixed cart management interface; issue #113

0.6.0 beta 3 (2011-11-26)
-------------------------

* Added: add log message when uploading of an image failed
* Bugfix: fixed display of average score in rating portlet
* Bugfix: fixed links to images within image gallery
* Bugfix: fixed changing state and deleting of orders; issue #110
* Bugfix: fixed display price if it's 0.0; issue #108

0.6.0 beta 2 (2011-11-21)
-------------------------
* Fixed display of portlets (using django-portlets 1.1)

0.6.0 beta 1 (2011-11-19)
-------------------------

* Using Django 1.3
* Added country dependent addresses
* Added pluggable price calculation
* Added supplier management
* Massively improved management interface
* Improved static file handling (Django's staticfiles)
* Improved properties management
* Removed SWFUpload (Flash) in favour of jquery.fileupload (Javascript)
* Using Python's locale to display currencies
* New contact form

HISTORY
=======

For the complete history please look into HISTORY.txt
