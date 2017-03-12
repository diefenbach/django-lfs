.. index:: Settings

.. _settings:

========
Settings
========

These are settings specific for LFS which can be changed within
``lfs_project/settings``. For Django's default settings which are also relevant
for LFS, please visit `Django settings
<http://docs.djangoproject.com/en/dev/ref/settings/>`_ for an explanation.


.. _settings_plugins:

Plug-ins
========

.. _settings_lfs_order_numbers_generators:

LFS_ORDER_NUMBER_GENERATOR
    The class which is responsible for the creation of order numbers. LFS ships
    with: ``lfs_order_numbers.models.OrderNumberGenerator``.

    .. seealso::

        :doc:`/developer/howtos/how_to_add_own_order_numbers/index`

.. _settings_lfs_payment_method_processors:

LFS_PAYMENT_METHOD_PROCESSORS
    List of list of available 3rd-party payment method processors, whereas the
    first entry is the dotted name to a PaymentMethod and the second entry is
    the name, which  is displayed. These are provided for selection within the
    payment method management interface, e.g.::

        LFS_PAYMENT_METHOD_PROCESSORS = [
            ["acme.ACMEPaymentMethod", _(u"ACME payment")],
        ]

    .. seealso::

         :doc:`/developer/howtos/how_to_add_own_payment_methods`

.. _settings_lfs_price_calculators:

LFS_PRICE_CALCULATORS
    List of list of available price calculators, whereas the first entry is the
    dotted name to a PriceCalculator and the second entry is the name, which is
    displayed. These are provided for selection within the shop preferences and
    the product. LFS is shipped with following entries::

        LFS_PRICE_CALCULATORS = [
            ["lfs.gross_price.calculator.GrossPriceCalculator", _(u"Price includes tax")],
            ["lfs.net_price.calculator.NetPriceCalculator", _(u"Price excludes tax")],
        ]

    .. seealso::

         :doc:`/developer/howtos/how_to_add_product_pricing`

.. _settings_lfs_shipping_price_calculators:

LFS_SHIPPING_METHOD_PRICE_CALCULATORS
    List of list of available shipping method price calculators, whereas the
    first entry is the dotted name to a ShippingMethodPriceCalculator and the
    second entry is the name, which is displayed. These are provided for
    selection within the shipping method. LFS is shipped with following
    entries::

        LFS_SHIPPING_METHOD_PRICE_CALCULATORS = [
            ["lfs.shipping.GrossShippingMethodPriceCalculator", _(u'Price includes tax')],
            ["lfs.shipping.NetShippingMethodPriceCalculator", _(u'Price excludes tax')],
        ]

    .. seealso::

        :doc:`/developer/howtos/how_to_shipping_price`

.. _settings_miscellaneous:

Miscellaneous
=============

LFS_AFTER_ADD_TO_CART
    URL name to which LFS redirects after the customer has put a product into
    the cart. LFS ships with ``lfs_added_to_cart``, which displays the last
    product, which has been added to the cart. A reasonable alternative is
    ``lfs_checkout_dispatcher``, which redirects directly to the checkout view.

.. _settings_lfs_criteria:

LFS_CRITERIA
    List of list of available criteria, whereas the first entry is the dotted
    name to a criterion and the second entry is the name of the criterion, which
    is displayed to the users. These criteria are provided to a :term:`shop
    manager` for selection for on several locations. LFS is shipped with
    following criteria::

        LFS_CRITERIA = [
            ["lfs.criteria.models.CartPriceCriterion", _(u"Cart Price")],
            ["lfs.criteria.models.CombinedLengthAndGirthCriterion", _(u"Combined Length and Girth")],
            ["lfs.criteria.models.CountryCriterion", _(u"Country")],
            ["lfs.criteria.models.HeightCriterion", _(u"Height")],
            ["lfs.criteria.models.LengthCriterion", _(u"Length")],
            ["lfs.criteria.models.WidthCriterion", _(u"Width")],
            ["lfs.criteria.models.WeightCriterion", _(u"Weight")],
            ["lfs.criteria.models.ShippingMethodCriterion", _(u"Shipping Method")],
            ["lfs.criteria.models.PaymentMethodCriterion", _(u"Payment Method")],
        ]

    .. seealso::

        :doc:`Concept of criteria </user/concepts/criteria>`, :doc:`How to add own criteria </developer/howtos/how_to_add_own_criteria/index>`

LFS_DELETE_IMAGES
    If this is set to True images on the file system are going to be deleted
    after an image has been deleted via the management interface, otherwise they
    are left untouched. This setting is optional, the default value is ``True``.

LFS_DELETE_FILES
    If this is set to True files on the file system are going to be deleted
    after an file/attachment has been deleted via the management interface,
    otherwise they are left untouched. This setting is optional, the default
    value is ``True``.

LFS_DOCS
    Base URL to the LFS docs. This is used for the context aware help link
    within the management interface. Defaults to
    http://docs.getlfs.com/en/latest/.

LFS_LOCALE
    Sets the locale for the shop, which is the base for number formatting and
    the displayed currency. If you don't set it, the current locale of your
    Python is not touched at all. Example::

        LFS_LOCALE = "en_US.UTF-8"

    .. seealso::

        http://en.wikipedia.org/wiki/Locale, http://docs.python.org/library/locale.html

LFS_LOG_FILE
    Absolute path to LFS' log file.

LFS_RECENT_PRODUCTS_LIMIT
    The amount of recent products which are displayed within the recent
    products portlet, e.g. 3.


.. _settings_orders:

Orders
======

LFS_EXTRA_ORDER_STATES
    Extra states for orders, eg. if you need to mark order as Delivered or such. Should be list of tuples, each
    containing id and label. Note that id should start from high number (20 or higher) to avoid conflicts if some new
    ORDER_STATES are added to LFS core. Example value might be: [(20, _('Delivered'))]

    There is a signal: order_state_changed that is sent when order state was changed and can be used for some special
    processing.

    .. code-block:: python

        def handle_order_state_changed(sender, order, request, old_state, **kwargs):
            pass
        order_state_changed.connect(handle_order_state_changed)


LFS_ONE_PAGE_CHECKOUT_FORM
    The form which is used at checkout page. This setting is optional, the
    default value is ``lfs.checkout.forms.OnePageCheckoutForm``.



.. _settings_addresses:

Addresses
=========

LFS_AUTO_UPDATE_DEFAULT_ADDRESSES
    If True then default shipping and invoice addresses (set
    by customer in his account settings) are automatically updated to the values
    from last order. Else, default addresses are untouched and are used
    as defaults in every new order. This setting is optional, the default value
    is ``True``.

LFS_CHECKOUT_NOT_REQUIRED_ADDRESS
    During checkout it is possible to not fill in one of the addresses - it will be then copied from another one.
    By default Shipping address is same as Invoice address, but it can be changed with this setting.
    Possible values are: ``shipping`` and ``invoice``. Default is ``shipping``.
    Note that you'll have to manually change checkout page template and lfs.js if you change it to ``invoice``.

    By default checkout_form (used at one_page_checkout.html) has method: ``no_address_field`` that will return either
    ``no_shipping`` or ``no_invoice`` field, depending on this setting.

Plugins
-------

LFS_ADDRESS_MODEL
    The model which is used to store addresses. This setting is optional, the
    default value is ``lfs.addresses.models.Address``.

LFS_INVOICE_ADDRESS_FORM
    The form which is used for shipping addresses. This setting is optional, the
    default value is ``lfs.addresses.forms.InvoiceAddressForm``.

LFS_SHIPPING_ADDRESS_FORM
    The form which is used for shipping addresses. This setting is optional, the
    default value is ``lfs.addresses.forms.ShippingAddressForm``.

.. seealso::

    :ref:`how_to_add_own_addresses`

Required fields
---------------

LFS_INVOICE_COMPANY_NAME_REQUIRED
    If True the company name of the invoice address is required. This setting is
    optional, the default value is ``False``.

LFS_INVOICE_EMAIL_REQUIRED
    If True the e-mail of the shipping address is required. This setting is
    optional, the default value is ``True``.

LFS_INVOICE_PHONE_REQUIRED
    If True the phone of the invoice address is required. This setting is
    optional, the default value is ``True``.

LFS_SHIPPING_COMPANY_NAME_REQUIRED
    If True the company name of the shipping address is required. This setting is
    optional, the default value is ``False``.

LFS_SHIPPING_PHONE_REQUIRED
    If True the phone of the shipping address is required. This setting is
    optional, the default value is ``False``.

LFS_SHIPPING_EMAIL_REQUIRED
    If True the e-mail of the shipping address is required. This setting is
    optional, the default value is ``False``.

.. _settings_units:

Units
=====

LFS_UNITS
    A list of available units for the product.

LFS_PRICE_UNITS
    A list of available units for the product price.

LFS_BASE_PRICE_UNITS
    A list of available units for the product base price.

LFS_PACKING_UNITS
    A list of available units for the product packaging.

.. _settings_email:

E-Mails
=======

LFS_SEND_ORDER_MAIL_ON_CHECKOUT
    If true, an e-mail with the order details is send to the customer after
    customer completes checkout screen.

LFS_SEND_ORDER_MAIL_ON_PAYMENT
    If true, an e-mail is send to the customer after the customer successfully
    pays for an order


.. _settings_sitemaps:

Sitemaps
========

LFS_SITEMAPS
    A dictionary which defines several settings for sitemaps. There are four
    sitemaps: ``category``, ``page``, ``product`` and ``shop``. Each of them can
    have four different settings: ``sitemap``, ``changefreq``, ``priority`` and
    ``protocol``. All sitemaps and settings are optional. If not given the
    default settings are used, which are::

     LFS_SITEMAPS = {
         "product": {
             "sitemap": "lfs.core.sitemaps.ProductSitemap",
             "changefreq": "weekly",
             "priority": 0.5,
             "protocol": "http",
         },
         "category": {
             "sitemap": "lfs.core.sitemaps.CategorySitemap",
             "changefreq": "weekly",
             "priority": 0.5,
             "protocol": "http",
         },
         "page": {
             "sitemap": "lfs.core.sitemaps.PageSitemap",
             "changefreq": "weekly",
             "priority": 0.5,
             "protocol": "http",
         },
         "shop": {
             "sitemap": "lfs.core.sitemaps.ShopSitemap",
             "changefreq": "weekly",
             "priority": 0.5,
             "protocol": "http",
         },
     }

    The following example means, you implement your own ``ProductSitemap``
    within ``myapp.sitemap`` and set the protocol for the default ones to
    ``https``::

     LFS_SITEMAPS = {
         "product": {
             "sitemap": "myapp.sitemap.ProductSitemap",
         },
         "category": {
             "protocol": "https",
         },
         "page": {
             "protocol": "https",
         },
         "shop": {
             "protocol": "https",
         },
     }

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

