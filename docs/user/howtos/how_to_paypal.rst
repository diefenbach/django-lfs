.. index:: PayPal

===================
How To Setup PayPal
===================

In this how-to you connect the shop to PayPal with the add-on lfs-paypal (2.x). The customer pays on PayPal's page
and comes back to the shop, which then creates the order.

Install lfs-paypal
==================

#. Install the package: ``pip install lfs-paypal`` (with lfs-starter: ``uv sync --extra paypal``).

#. Add ``"lfs_paypal"`` to ``INSTALLED_APPS`` (after ``*LFS_APPS``) and its URLs to ``urls.py``::

    path("paypal/", include("lfs_paypal.urls")),

#. Offer its processor to payment methods::

    LFS_PAYMENT_METHOD_PROCESSORS = [
        ["lfs_paypal.processor.PayPalProcessor", _("PayPal")],
    ]

#. Run ``python manage.py migrate``.

Get the credentials
===================

#. Log in at https://developer.paypal.com/ with your PayPal business account.

#. Under ``Apps & Credentials`` create an app in the **Sandbox**. Its ``Client ID`` and ``Secret`` go into the
   settings (from environment variables, not into the code)::

    PAYPAL_MODE = "sandbox"
    PAYPAL_CLIENT_ID = "..."
    PAYPAL_CLIENT_SECRET = "..."

Add the payment method
======================

A shop set up with ``lfs_init`` while lfs-paypal was installed already has the payment method ``PayPal``.
Otherwise:

#. Go to ``Shop / Payment Methods`` and click ``Add Payment Method``; name it ``PayPal``.

#. On the ``Data`` tab check ``Active``, select the ``Module`` ``PayPal``, and click ``Save payment method``.

Test and go live
================

#. Order something in the shop and pay with a sandbox buyer account (``Sandbox accounts`` in the developer
   dashboard). After the payment PayPal sends the customer back to the shop, which shows the thank-you page and
   sends the order mails.

#. To go live, create an app under ``Live`` in the developer dashboard and set its ``Client ID`` and ``Secret``
   together with ``PAYPAL_MODE = "live"``.

.. note::

    lfs-paypal charges in EUR.

See Also
========

* :doc:`how_to_payment_method`
* :ref:`Settings of lfs-paypal <settings_paypal>`
