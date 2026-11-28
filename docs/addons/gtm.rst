.. index:: Google Tag Manager

============================
Google Tag Manager (lfs-gtm)
============================

Loads your Google Tag Manager container with Google Consent Mode v2 and pushes the e-commerce events of the shop to
the ``dataLayer``: ``view_item_list``, ``view_item``, ``add_to_cart``, ``begin_checkout`` and ``purchase``.

Installation
============

lfs-gtm needs :doc:`cookie_consent` (pip installs it): without consent GTM tracks nothing.

.. code-block:: python

    INSTALLED_APPS = [..., "lfs_cookie_consent", "lfs_gtm"]

    GTM_ID = "GTM-XXXXXXX"

Without ``GTM_ID`` nothing is rendered, so you can install the add-on everywhere and set the ID only in production.

How it works
============

* Until the visitor agrees, Consent Mode denies analytics and advertising. When the visitor saves a choice in the
  banner, lfs-gtm passes it to Google and removes the cookies of a declined category.
* The events carry the products, prices and the order in the GA4 format. Which tags fire on them (e.g. GA4) you set
  up in your GTM container; the README of lfs-gtm describes the container.

lfs-theme includes everything once the add-on is installed.
