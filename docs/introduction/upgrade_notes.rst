.. index:: Upgrade notes

=============
Upgrade notes
=============
Below is a description of changes that are useful to know about when upgrading LFS to newer version


Upgrading from 0.7.x to 0.8.x
=============================

This is not full reference of changes but at least some of them are described:

* currency templatetag always returns HTML now, eg. <span class="money">Fr. 999</span>, previously HTML was only returned for negative values
* currency templatetag in text email templates (lfs_theme/templates/lfs/mail/order_details.txt) was removed in favour of currency_text templatetag. The latter one doesn't return HTML (ever).
* lfs/base.html has slightly different structure to the footer and colophon sections due to incorrect width of these elements in previous layout.
  div.colophon-inner and div.footer-inner html elements were added, both with padding: 10px set in main.css.
  padding: 10px was removed from '#footer .container' and '#colophon .container' in main.css
* update_editor method in lfs_tinymce.js has been modified and requires tinymce 3.5.8 which is now being used.
  References to tinymce were changed in manage_base.html and lfs_tinymce.js
* filter portlet has been updated to allow for manufacturer filtering and because of that its template:
  lfs_theme/templates/lfs/portlets/filter.html was modified - manufacturer filtering section has been added
* Small change at lfs/templates/manage/product/product.html - removed onkeypress from filter input element in favour
  of css class 'disable-enter-key'. Changed lfs.manage.js to add event handler for 'disable-enter-key'.
* Added new ORDER state: PREPARED that can be used to mark orders as prepared to be sent.
* Added new signal and setting that allows defining extra ORDER_STATES. Signal is order_state_changed and option is
  LFS_EXTRA_ORDER_STATES. New states should start with id 20 or higher to avoid conflicts with built in states.
* Use 'SHOP' instead of 'shop' in lfs/shop/shop.html
* Added position column to PropertyGroups and ability to order these with drag & drop in management panel - modified lfs.manage.js
  and management template for property groups.
* Added LFS_CHECKOUT_NOT_REQUIRED_ADDRESS setting. This allows to change address that is not required at checkout page.
  Changed one_page_checkout.html template, lfs.js and OnePageCheckout Form.
* refactored lfs.manage.js - do not use ``live`` anymore. Updated manage/export/export.html, manage/export/export_inline.html,
  manage/manufactuers/manufacturer.html and manage/manufacturers/manufacturer_inline.html to use data-url instead of just 'data'
  and use elem.data('something') in JavaScript
* added <div id="portlets-dialog" title="{% trans "Portlets dialog" %}"></div> to manage_base.html to handle properly inerting images to TinyMCE within portlets dialog
  (changes to lfs.manage.js with portlets dialog)
* added some SEO related attributes to templates and canonical tags for variants
* modified catalog/views.py -> category_products and catalog/views.py -> category_categories return value, so that it now contains
  pagination data for use in main template (SEO optimization with rel="next/prev" (template: lfs/catalog/category_base.html)
* modified mimetype returned by ajax calls to: application/json. This requireS changes in javascript ajax calls:
  lfs.js, lfs.manage.js, lfs_tinymce.js, manage/product/attachments.html(!)
* moved javascript code from manage/product/images.html to lfs.manage.product.js and updated to use proper mimetypes in responses