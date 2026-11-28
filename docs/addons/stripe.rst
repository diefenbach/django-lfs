.. index:: Stripe

======================================
Card payments with Stripe (lfs-stripe)
======================================

Customers pay by card on the checkout page; the card data goes directly to Stripe, never through the shop.

Installation
============

.. code-block:: python

    INSTALLED_APPS = [..., "lfs_stripe"]

    STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]            # sk_..., stays on the server
    STRIPE_PUBLISHABLE_KEY = os.environ["STRIPE_PUBLISHABLE_KEY"]  # pk_..., sent to the browser
    STRIPE_SHOP_NAME = "My shop"  # prefix of the references shown in Stripe

    # urls.py: the checkout script calls these paths, so the prefix must be stripe/
    path("stripe/", include("lfs_stripe.urls")),

Both keys come from the Stripe dashboard (``Developers / API keys``) and must belong to the same account; use the
test keys first. Read them from environment variables, never put them into the code.

The payment method
==================

Under ``Shop / Payment Methods`` add a payment method, e.g. ``Credit card``, and select the ``Type`` ``Credit
Card``; leave ``Module`` empty. lfs-theme then shows the card fields of Stripe on the checkout page when the
customer selects this payment method.

How a payment works
===================

#. The checkout page loads the publishable key from ``/stripe/config/`` and shows the card fields.
#. When the customer buys, the shop creates a payment of the cart total at Stripe (with the secret key, so the
   amount cannot be changed in the browser), and the browser confirms it with Stripe.
#. On success the shop creates the order and shows the thank-you page.

.. note::

    Payments are in EUR. If the checkout page shows no card fields, check that ``STRIPE_PUBLISHABLE_KEY`` is set:
    without it ``/stripe/config/`` fails.
