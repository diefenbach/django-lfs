.. index:: Cookie consent

===================================
Cookie consent (lfs-cookie-consent)
===================================

A banner that asks visitors for their consent to analytics and advertising cookies, with a dialog for the details.
The choice is stored in the cookie ``cookie-consent``.

The add-on loads no tracking itself. Install it together with a tracking add-on such as :doc:`gtm`, or with
scripts of your own that listen to the browser event ``lfs:consent-changed``. A shop without tracking sets only the
cookies it needs (session, CSRF) and needs no banner.

Installation
============

.. code-block:: python

    INSTALLED_APPS = [..., "lfs_cookie_consent"]

lfs-theme then shows the banner and a link to change the settings. A theme of your own uses the tags
``{% cookie_banner %}`` and ``{% cookie_modal %}`` of ``lfs_cookie_consent_tags`` and the script
``lfs_cookie_consent/lfs_cookie_consent.js`` (see the README of lfs-cookie-consent).
