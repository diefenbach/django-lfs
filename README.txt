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

0.6.15 (2012-04-30)
-------------------

* Bugfix: fixed management of criteria
* Bugfix: fixed display of image for category sub-categories view
* Changed: added 100x100px box to search results to prevent content jumping from left to right when the page is loaded (naro)
* Changed: clean up display of package result

0.6.14 (2012-04-21)
-------------------

* Bugfix: fixed display prices for properties (Maciej Wiśniowski)
* Bugfix: fixed TinyMCE for several browsers (Maciej Wiśniowski)
* Bugfix: display credit card fields if the type of the selected payment method is credit card; #issue: 191

0.6.13 (2012-04-08)
-------------------

* Bugfix: display ``displayed properties`` in the correct order py positions; issue #184
* Bugfix: display property options in the correct order by positions within filter portlet

0.6.12 (2012-03-31)
-------------------

* Bugfix: fixed local variable 'message' referenced before assignment (Maciej Wiśniowski)
* Bugfix: fixed CreditCard's __unicode__ method; issue #172
* Bugfix: added safe filter to static block; issue #174

0.6.11 (2012-03-24)
-------------------

* Bugfix: added csrf token to password reset forms; issue #170
* Bugfix: removed double slash from logo URLs; issue #166
* Updated German translations

0.6.10 (2012-03-17)
-------------------

* Using django-postal 0.9
* Bugfix: don't display non-active products within cart nor add them to order with checkout; adapt tests; fixed issue #154.
* Bugfix: don't delete OrderItems when a product is deleted.

0.6.9 (2012-03-08)
------------------

* Security fix
* Added manufacturer field to product management (Maciej Wiśniowski)
* Bugfix: fixed pagination for product page; issue #152 (Maciej Wiśniowski)
* Bugfix: fixed deleting of image for payment and shipping methods; issue #150
* Bugfix: fixed markup; #issue #148

0.6.8 (2012-03-03)
------------------

* Bugfix: fixed duplicate labels and invalid tags (Maciej Wiśniowski)
* Bugfix: fixed calculation of topsellers when order items has no product (Maciej Wiśniowski)
* Updated polish translations (Maciej Wiśniowski)
* Updated german translations

0.6.7 (2012-02-26)
------------------

* Bugfix: fixed displaying of manual topsellers (Maciej Wiśniowski)
* Bugfix: topsellers - avoid empty product_id for discounts (Maciej Wiśniowski)
* Bugfix: take care of variants for deliverability (Maciej Wiśniowski)
* Bugfix: fixed bug causing strange behaviour while creating variants (Maciej Wiśniowski)
* Bugfix: fixed product filtering for product management views; #issue 142
* Bugfix: added csrf token to active-images-update-form
* Bugfix: fixed lfs_init for Postgres; issue #129
* Added translations for filter buttons and fix for topseller positions (Maciej Wiśniowski)
* Updated polish translations (Maciej Wiśniowski)
* Updated german translations

0.6.6 (2012-02-09)
------------------

* Bugfix: fixed url for Pages at breadcrums (Maciej Wiśniowski)
* Bugfix: display sale price at category products page (Maciej Wiśniowski)
* Bugfix: fix product pagination (Maciej Wiśniowski)
* Bugfix: added short_description to Category management UI
* Bugfix: display category descriptions
* Bugfix: fixed template selection; issue #134
* Improvement: allow easy modification of category/product templates (Maciej Wiśniowski)
* Updated polish translations (Maciej Wiśniowski)

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
