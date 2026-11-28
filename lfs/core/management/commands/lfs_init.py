"""Management command lfs_init: fill an empty database with a working shop."""

from django.apps import apps
from django.core.management.base import BaseCommand
from lfs.settings import lfs_setting

SHOP_DESCRIPTION = """
<h1 class="first-heading">Welcome to LFS!</h1>
<p>LFS is an online shop based on <a href="https://www.python.org/">Python</a> and
<a href="https://www.djangoproject.com/">Django</a>.</p>

<h2>Get started</h2>
<p>Go to the <a href="/manage/dashboard/">management interface</a> to add categories, products, and pages.
This text is the shop's description; you can change it there under Shop.</p>

<h2>Information &amp; help</h2>
<ul>
<li><a href="https://github.com/diefenbach/django-lfs">Source code and issues on GitHub</a></li>
</ul>
"""


class Command(BaseCommand):
    """Set up a fresh shop: ``python manage.py lfs_init``."""

    args = ""
    help = "Initializes LFS"

    def handle(self, *args: str, **options: object) -> None:
        """Create the shop with its default data in the database.

        Creates the shop, countries, delivery times, the action groups with their actions, the portlet slots (without
        portlets), payment methods (PayPal only when lfs_paypal is installed), shipping methods, pages, and the order
        number generator.
        """
        from lfs.catalog.models import DeliveryTime
        from lfs.catalog.settings import DELIVERY_TIME_UNIT_DAYS
        from lfs.core.models import ActionGroup
        from lfs.core.models import Action
        from lfs.core.models import Application
        from lfs.core.models import Country
        from lfs.core.models import Shop
        from lfs.core.utils import import_symbol

        from portlets.models import Slot

        from lfs.payment.models import PaymentMethod
        from lfs.payment.settings import PM_BANK
        from lfs.page.models import Page
        from lfs.shipping.models import ShippingMethod

        # Country
        usa = Country.objects.create(code="us", name="USA")

        # Default delivery time
        delivery_time = DeliveryTime.objects.create(min=1, max=2, unit=DELIVERY_TIME_UNIT_DAYS)

        # Shop
        shop = Shop.objects.create(
            name="LFS",
            shop_owner="John Doe",
            from_email="john@doe.com",
            notification_emails="john@doe.com",
            description=SHOP_DESCRIPTION,
            default_country=usa,
            delivery_time=delivery_time,
        )
        shop.invoice_countries.add(usa)
        shop.shipping_countries.add(usa)

        # Actions
        tabs = ActionGroup.objects.create(name="Tabs")
        footer = ActionGroup.objects.create(name="Footer")
        Action.objects.create(group=tabs, title="Contact", link="/contact", active=True, position=1)
        Action.objects.create(
            group=footer, title="Terms and Conditions", link="/page/terms-and-conditions", active=True, position=1
        )
        Action.objects.create(group=footer, title="Imprint", link="/page/imprint", active=True, position=2)

        # Slots for portlets. The default theme navigates with menus, so no portlets are assigned.
        Slot.objects.create(name="Left")
        Slot.objects.create(name="Right")

        # Payment methods
        PaymentMethod.objects.create(name="Direct debit", priority=1, active=1, deletable=0, type=PM_BANK)
        PaymentMethod.objects.create(name="Cash on delivery", priority=2, active=1, deletable=0)
        if apps.is_installed("lfs_paypal"):
            PaymentMethod.objects.create(
                name="PayPal", priority=3, active=1, deletable=0, module="lfs_paypal.processor.PayPalProcessor"
            )
        PaymentMethod.objects.create(name="Prepayment", priority=4, active=1, deletable=0)

        # Shipping methods
        ShippingMethod.objects.create(name="Standard", priority=1, active=1)

        # Pages
        p = Page.objects.create(title="Root", slug="", active=1, exclude_from_navigation=1)
        p.id = 1
        p.save()
        p = Page.objects.create(
            title="Terms and Conditions",
            slug="terms-and-conditions",
            active=1,
            body="Enter your terms and conditions here.",
        )
        p.id = 2
        p.save()
        p = Page.objects.create(title="Imprint", slug="imprint", active=1, body="Enter your imprint here.")
        p.id = 3
        p.save()

        # Order Numbers
        ong = import_symbol(lfs_setting("LFS_ORDER_NUMBER_GENERATOR"))
        ong.objects.create(id="order_number")

        # Application object
        Application.objects.create(version="0.7")
