.. index:: Settings

.. _settings:

========
Settings
========

These are settings specific for LFS. For Django's default settings which are
relevant for LFS (within ``lfs_project/settings``) please visit `Django settings
<http://docs.djangoproject.com/en/dev/ref/settings/>`_ for an explanation.

.. _settings_miscellaneous:

Miscellaneous
=============

LFS_RECENT_PRODUCTS_LIMIT
    The amount of recent products which are displayed within the recent
    products portlet, e.g. 3.

LFS_APP_ORDER_NUMBERS
    The APP which is responsible for the creation of order numbers. Defaults
    to: ``lfs_order_numbers``.

LFS_DOCS
    Base URL to the LFS docs. This is used for the context aware help link
    within the management interface. Defaults to
    http://docs.getlfs.com/en/latest/.

.. _settings_lfs_payment_modules:

LFS_PAYMENT_MODULES
    List of list of available 3rd-party payment modules, whereas the first entry
    is the dotted name to a PaymentMethod and the second entry is the name,
    which  is displayed. These are provided for selection within the payment
    method management interface, e.g.::

        LFS_PAYMENT_MODULES = [
            ["acme.ACMEPaymentMethod", "ACME payment"],
        ]

    See also :doc:`/developer/howtos/how_to_add_own_payment_methods`.

.. _settings_email:

E-Mail
======

LFS_SEND_ORDER_MAIL_ON_CHECKOUT
    If true, an e-mail with the order details is send to the customer after
    customer completes checkout screen.

LFS_SEND_ORDER_MAIL_ON_PAYMENT
    If true, an e-mail is send to the customer after the customer successfully
    pays for an order

.. _settings_reviews:

Reviews
=======

REVIEWS_SHOW_PREVIEW
    True or False. If True the user will see a preview of his review.

REVIEWS_IS_NAME_REQUIRED
    True or False. If True the name of the review is required.

REVIEWS_IS_EMAIL_REQUIRED
    True or False. If True the name of the e-mail is required.

REVIEWS_IS_MODERATED
    True or False. If True the review must be moderated and published before it
    is public.

.. _settings_paypal:

PayPal
======

PAYPAL_RECEIVER_EMAIL
    Your PayPal id, e.g. info@getlfs.com.

PAYPAL_IDENTITY_TOKEN
    PayPal's PDT identity token.

LFS_PAYPAL_REDIRECT
    True or False. If True the customer is automatically redirected to PayPal
    after he submitted his order. If False the thank-you page is displayed
    with a link to PayPal.

