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

0.7.0 beta 7 (2012-04-08)
-------------------------

* Bugfix: display ``displayed properties`` in the correct order py positions; issue #184
* Bugfix: display property options in the correct order by positions within filter portlet
* Bugfix: fixed image presentation directly after upload within shop management interface (Maciej Wiśniowski)
* Bugfix: fixed display of discounts
* New: added variants tab to documentation
* Updated Polish translations (Maciej Wiśniowski)
* Updated German translations

0.7.0 beta 6 (2012-03-31)
-------------------------

* Bugfix: added safe filter to static block; issue #174 (Frank Feng)
* Bugfix: Fixed display of short description for variants
* Bugfix: fixed decimal_l10n tag: return origin value if it's no float
* Bugfix: fixed error messages within checkout; issue #176 (Maciej Wiśniowski)
* Bugfix: fixed __unicode__ methods of several models; issue #172
* Bugfix: fixed positions of newly added variants (Maciej Wiśniowski)
* Bugfix: fixed layout, when there are no portlets at right; issue #173 (Frank Feng)
* Bugfix: fixed local variable 'message' referenced before assignment (Maciej Wiśniowski)
* Updated: Polish translations (Maciej Wiśniowski)
* Updated: Chinese translations (Frank Feng)
* Updated: German translations

0.7.0 beta 5 (2012-03-24)
-------------------------

* Bugfix: added csrf token to password reset forms; issue #170
* Bugfix: prevent setting of unsupported locale; #issue 165.
* Bugfix: removed double slash from logo URLs; issue #166
* Updated German translations

0.7.0 beta 4 (2012-03-21)
-------------------------

* Bugfix: fixed edit/view product urls; issue #164 (Frank Feng)
* Bugfix: removed typo; issue #163 (Frank Feng)
* Bugfix: fixed accessories tab in manage; #issue #162 (Frank Feng)
* Bugfix: get_base_price_net; #issue #161
* Bugfix: display only parent's active base price value for variants
* Bugfix: take the parent's price calculator for variants
* Added: Chinese translations (Frank Feng)
* Added: default footer for email messages (Maciej Wiśniowski)
* Improved: page pagination for category products view (Maciej Wiśniowski)
* Improved: email templates (Maciej Wiśniowski)
* Updated: German translations
* Updated: Polish translations (Maciej Wiśniowski)

0.7.0 beta 3 (2012-03-18)
-------------------------

* Bugfix: fixed number of columns within cart template (Maciej Wiśniowski)
* Bugfix: fixed display of localized amount of items within cart portlet; issue #159
* Bugfix: don't display non-active products within cart nor add them to order with checkout; adapt tests; fixed issue #154
* Bugfix: don't delete OrderItems when a product is deleted
* Bugfix: added default values for LFS_SHIPPING_* settings
* Bugfix: removed redundant javascript code; issue #153
* Changed: using django-postal 0.9
* Changed: removed djangorestframework from dependencies
* Improved: added label to PropertyGroup's name field; issue #158
* Improved: added link to product within order detail view in LM; issue #149
* Improved: cleaned up displaying of addresses of orders within LM
* Updated: Czech translation (naro)
* Updated: German translation
* Updated: Polish translations (Maciej Wiśniowski)

0.7.0 beta 2 (2012-03-08)
-------------------------

* Security fix
* Added manufacturer field to product management (Maciej Wiśniowski)
* Bugfix: fixed pagination for product page; issue #152 (Maciej Wiśniowski)
* Bugfix: fixed deleting of image for payment and shipping methods; issue #150
* Bugfix: fixed markup; #issue #148
* Bugfix: fixed updating of attachments; issue #147
* Improved javascript: prevent FOUC for category-tabs and manage-tabs;

0.7.0 beta 1 (2012-03-03)
-------------------------

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
