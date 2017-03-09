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

Development
===========

For development environment please visit:

* https://github.com/diefenbach/lfs-buildout-development

Changes
=======

0.11.0 (2017-03-09)
-------------------
* Adds Django 1.10 support
* Excludes variants from sitemap
* Add appending slash to all urls
* Use F() expressions to update stock amount (#203)
* Use F() expression to increase use_amount for vouchers (#202)
* Removes django-pagination (use Django's default one instead)
* remove STATIC_URL (user static_url tag instead)
* fix saving properties and variant prices [pigletto]

0.10.2 (2015-04-25)
-------------------
* Updates lfs-paypal to 1.3
* Fixes all tests

0.10.1 (2015-04-23)
-------------------
* Fixes MANIFEST.in
* Fixes adding and display of reviews when L10N is turned on

0.10.0 (2015-04-22)
-------------------
* Adds Django 1.8 support
* Moves static files to lfs.manage
* Moves manage templates to lfs.manage

HISTORY
=======

For the complete history please look into HISTORY.txt
