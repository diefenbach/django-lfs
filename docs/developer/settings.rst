.. index:: Settings

.. _settings:

========
Settings
========

These are settings specific for LFS which can be changed within
``lfs_project/settings``. For Django's default settings which are also relevant
for LFS, please visit `Django settings
<http://docs.djangoproject.com/en/dev/ref/settings/>`_ for an explanation.

.. _settings_miscellaneous:

Miscellaneous
=============

LFS_AFTER_ADD_TO_CART
    URL name to which LFS redirects after the customer has put a product into
    the cart. LFS ships with ``lfs_added_to_cart``, which displays the last
    product, which has been added to the cart. A reasonable alternativ is
    ``lfs_checkout_dispatcher``, which redirects directly to the checkout view.

LFS_APP_ORDER_NUMBERS
    The APP which is responsible for the creation of order numbers. Defaults
    to: ``lfs_order_numbers``.

LFS_DOCS
    Base URL to the LFS docs. This is used for the context aware help link
    within the management interface. Defaults to
    http://docs.getlfs.com/en/latest/.

LFS_LOG_FILE
    Absolute path to LFS' log file.

.. _settings_lfs_payment_modules:

LFS_PAYMENT_MODULES
    List of list of available 3rd-party payment modules, whereas the first entry
    is the dotted name to a PaymentMethod and the second entry is the name,
    which  is displayed. These are provided for selection within the payment
    method management interface, e.g.::

        LFS_PAYMENT_MODULES = [
            ["acme.ACMEPaymentMethod", _(u"ACME payment")],
        ]

    See also :doc:`/developer/howtos/how_to_add_own_payment_methods`.

LFS_PRICE_CALCULATORS
    List of list of available price calculators, whereas the first entry is the
    dotted name to a PriceCalculator and the second entry is the name, which  is
    displayed. These are provided for selection within the shop preferences and
    the product. LFS is shipped with following entries::

        LFS_PRICE_CALCULATORS = [
            ["lfs.gross_price.GrossPriceCalculator", _(u"Price includes tax")],
            ["lfs.net_price.NetPriceCalculator", _(u"Price excludes tax")],
        ]

    See also :doc:`/developer/howtos/how_to_add_product_pricing`.

LFS_RECENT_PRODUCTS_LIMIT
    The amount of recent products which are displayed within the recent
    products portlet, e.g. 3.

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

