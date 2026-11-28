.. index:: Carousel

=======================
Carousel (lfs-carousel)
=======================

A slider of images with title, text and link on the start page of the shop.

Installation
============

.. code-block:: python

    INSTALLED_APPS = [..., "lfs_carousel"]

    # urls.py
    from lfs_carousel.views import carousel

    urlpatterns += [path("carousel/", include(carousel.urls))]

Then run ``python manage.py migrate``.

Usage
=====

Under ``Shop / Preferences`` the add-on adds the tab ``Carousel``:

.. image:: /images/addon_carousel.png
   :alt: The Carousel tab of the shop preferences

#. Under ``Upload New Items`` select one or more images and click ``Upload Images``.
#. Under ``Carousel Items`` enter the ``Title``, ``Text``, ``URL`` and ``Position`` of each item and click ``Update
   Items``; select items and click ``Delete Selected`` to remove them.

Only users with the permission to manage the shop can change the carousel. lfs-theme shows it on the start page; a
theme of your own uses ``{% load lfs_carousel_tags %}`` and ``{% carousel_show shop %}``.
