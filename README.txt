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

* http://demo.getlfs.com

Changes
=======

0.5.2 (2012-04-08)
------------------

* Bugfix: display ``displayed properties`` in the correct order py positions; issue #184
* Bugfix: display property options in the correct order by positions within filter portlet

0.5.1 (2012-03-30)
------------------

* Bugfix: fixed upload of images and files.

0.5.0 (2012-03-08)
------------------

* Security fix

0.5.0 beta 8 (2011-06-25)
-------------------------

* Bugfix: pinned version of djangorecipe to 0.23.1
* Enhancement: added active_name and active_price to variants management view; issue #51
* Enhancement: cleaned up password reset templates

0.5.0 beta 7 (2011-04-13)
-------------------------

* Improved error message for checkout form (Andres Vargas / zodman); issue #87
* Fixed invalid HTML; issue #81
* Bugfix: correct display of cart within shop view after cart has been updated; issue #82
* Bugfix: save and display correct text of TextPortlets; issue #39
* Fixed requried permission from "manage_shop" to "core.manage_shop"; issue #84
* Fixed Integration Error when adding Product with existing slug; issue #42
* Bugfix: made option price optional (as stated within form)
* Updated documentation; issue #60
* Added transifex config file
* Added translations for mexican spanish (Andres Vargas)
* Updated spain translations
* Updated german translations

0.5.0 beta 6 (2010-10-16)
-------------------------

* Bugfix added_to_cart: Display correct taxes within added_to_cart view. Issue #65.
* Bugfix variants: display variant's properties on cart, added_to_cart, checkout, received_mail, sent_mail. Issue #40.
* Bugfix lfs.cart: fixed total of added_to_cart view. Issue: #38.
* Bugfix lfs.cart: subtract voucher price from cart price.
* Changed: provide own redirect middleware in order to redirect urls with query string.

0.5.0 beta 5 (2010-07-31)
-------------------------

* Bugfix add_to_cart: display correct stock amount if not enough products are within stock.
* Added more tests

0.5.0 beta 4 (2010-07-30)
-------------------------

* Bugfix pages: caching page_view
* Bugfix cart: display correct stock amount within growl message
* Bugfix product_inline: display property title within error message
* Bugfix order_received_mail.html: display the correct selected values of a configurable product
* Bugfix cart: calculation of maximum delivery date
* Bugfix redirect: save redirect url for variants
* Bugfix lfs.page.views: added missing import of Http404
* Bugfix: restrict adding to cart if the product is not deliverable. Issue #37
* Added french translations (Jacques Seite)
* Added get_properties method to OrderItem
* Added optional cached parameter to cart/utils/get_cart_price and cart/utils/get_cart_costs
* Removed javascript which dynamically sets the height of the slots.
* Changed properties management: display name instead of title within left portlet
* Improved lfs.portlet: caching

0.5.0 beta 3 (2010-06-30)
-------------------------

* Bugfix manage property form: display validators for float field
* Bugfix: Using property title instead of name
* Bugfix Product.get_variant_properties: display only variant properties
* Bugfix order_inline.html: display product.unit instead of price_unit;
  display title of property
* Bugfix cart: inject correct html after refresh the cart
* Check also for existing username within RegisterForm
* Take subject for new_user_mail from template
* Display default value for configurable properties

0.5.0 beta 2 (2010-06-27)
-------------------------

* Cleaned up contact form

0.5.0 beta 1 (2009-12-27)
-------------------------

* First public beta release
