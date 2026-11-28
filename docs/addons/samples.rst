.. index:: Samples

=====================
Samples (lfs-samples)
=====================

Customers order a sample of a product from its product page, e.g. a fabric or colour sample. A sample is an ordinary
product with its own price, stock and delivery; to give samples away, give them the price 0.

Installation
============

.. code-block:: python

    INSTALLED_APPS = [..., "lfs_samples"]

    # urls.py: required, the Samples tab links to these views
    path("manage/samples/", include("lfs_samples.urls")),

Then run ``python manage.py migrate``.

Usage
=====

Every product gets a ``Samples`` tab in the management interface.

#. Open the sample product, check ``Is sample`` and save.
#. Open the product that offers the sample. Under ``Selectable Samples`` select the samples and click ``Add to
   samples``; ``Selected Samples`` lists them, ``Remove from samples`` takes them away.
#. For a variant, ``Active samples`` decides whether it uses its own samples or those of its product.

lfs-theme shows the samples on the product page; a theme of your own uses the template tags of
``lfs_samples_tags`` (see the README of lfs-samples).
