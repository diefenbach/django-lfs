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