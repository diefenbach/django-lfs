.. index:: Settings

========
Settings
========

These are settings specific for LFS. For Django's default settings please
visit `Django settings <http://docs.djangoproject.com/en/dev/ref/settings/>`_.

.. Note::
    These settings might be dropped in favour of the shop preferences, see :doc:
    `/user/shop/preferences`.

Reviews
=======

REVIEWS_SHOW_PREVIEW
    True or False. If True the user will see a preview of his review.

REVIEWS_IS_NAME_REQUIRED
    True or False. If True the name of the review is required.

REVIEWS_IS_EMAIL_REQUIRED
    True or False. If True the name of the e-mail is required.

REVIEWS_IS_MODERATED
    True or False. If True the review must be moderated and published before
    it is public.

PayPal
======

PAYPAL_RECEIVER_EMAIL
    Your PayPal id, e.g. info@lfcproject.com

LFS_PAYPAL_REDIRECT
    True or False. If True the customer is automatically redirected to PayPal
    after he submitted his order. If False the thank-you page is displayed
    with a link to PayPal.

Miscellaneous
=============

LFS_RECENT_PRODUCTS_LIMIT
    The amount of recent products which are displayed within the recent
    products portlet, e.g. 3.

E-Mail
======

DEFAULT_FROM_EMAIL
    The sender e-mail address for the contact form.

LFS_SEND_ORDER_MAIL_ON_CHECKOUT
    Send details of order after customer completes checkout screen

LFS_SEND_ORDER_MAIL_ON_PAYMENT
    Send details of order after customer successfully pays for an order
