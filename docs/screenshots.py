"""Take the screenshots of the management interface for the documentation (``bin/screenshots``).

Sets up a throwaway shop with the test settings, fills it with demo data (a shop for kitchen textiles and
tableware), serves it on a free local port, and saves one PNG per entry of ``SHOTS`` into ``docs/images/``.
Run it again after a change to the management interface; the demo data is the same every time.
"""

import os
import sys
import tempfile
import threading
from collections.abc import Callable
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "docs" / "images"
WORK = Path(tempfile.mkdtemp(prefix="lfs-screenshots-"))

sys.path.insert(0, str(ROOT))
os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"

import tests.settings as test_settings  # noqa: E402

# A database file instead of the in-memory one, because the server runs in another thread.
test_settings.DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": WORK / "shop.sqlite3"}}
test_settings.MEDIA_ROOT = WORK / "media"
test_settings.ROOT_URLCONF = "docs_screenshot_urls"
test_settings.LANGUAGE_CODE = "en"

import django  # noqa: E402

django.setup()

from django.urls import include, path, re_path  # noqa: E402
from django.views.static import serve  # noqa: E402

# The test URLs plus the uploaded product images, which the test settings do not serve.
sys.modules["docs_screenshot_urls"] = type(sys)("docs_screenshot_urls")
sys.modules["docs_screenshot_urls"].urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": test_settings.MEDIA_ROOT}),
    path("", include("tests.urls")),
]

from django.contrib.auth.models import User  # noqa: E402
from django.contrib.contenttypes.models import ContentType  # noqa: E402
from reviews.models import Review  # noqa: E402

from lfs.addresses.models import Address  # noqa: E402
from lfs.cart.models import Cart, CartItem  # noqa: E402
from lfs.customer.models import Customer  # noqa: E402
from lfs.order.models import Order, OrderItem  # noqa: E402
from lfs.order.settings import PAID, SENT, SUBMITTED  # noqa: E402
from django.contrib.staticfiles.handlers import StaticFilesHandler  # noqa: E402
from django.core.files.base import ContentFile  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402
from django.test import Client  # noqa: E402
from PIL import Image as PILImage  # noqa: E402
from PIL import ImageDraw  # noqa: E402

from lfs.catalog.models import Category, Image, Product, Property, PropertyOption  # noqa: E402
from lfs.catalog.settings import PROPERTY_SELECT_FIELD  # noqa: E402
from lfs.core.models import Country, Shop  # noqa: E402
from lfs.discounts.models import Discount  # noqa: E402
from lfs.discounts.settings import DISCOUNT_TYPE_PERCENTAGE  # noqa: E402
from lfs.marketing.models import FeaturedProduct  # noqa: E402
from lfs.manufacturer.models import Manufacturer  # noqa: E402
from lfs.page.models import Page  # noqa: E402
from lfs.payment.models import PaymentMethod  # noqa: E402
from lfs.shipping.models import ShippingMethod  # noqa: E402
from lfs.tax.models import Tax  # noqa: E402

PASSWORD = "screenshots-only"

CATEGORIES = [("Kitchen textiles", "kitchen-textiles"), ("Knives", "knives"), ("Tableware", "tableware")]

# name, slug, SKU, price, category slug, colour of the generated product image, short description
PRODUCTS = [
    ("Linen apron, sage", "linen-apron-sage", "AP-1042-SG", "29.90", "kitchen-textiles", (156, 175, 136),
     "Washed linen, adjustable neck strap, two front pockets."),
    ("Linen apron, charcoal", "linen-apron-charcoal", "AP-1042-CH", "29.90", "kitchen-textiles", (70, 72, 76),
     "Washed linen in charcoal."),
    ("Tea towel, set of 3", "tea-towel-set", "TT-0310", "19.50", "kitchen-textiles", (214, 196, 160),
     "Half linen, 50 × 70 cm."),
    ("Bread knife 21 cm", "bread-knife-21", "KN-2100", "34.90", "knives", (160, 120, 84),
     "Serrated blade, beech handle."),
    ("Chef's knife 20 cm", "chefs-knife-20", "KN-2000", "79.00", "knives", (120, 92, 70),
     "Forged steel, full tang."),
    ("Stoneware plate, 27 cm", "stoneware-plate-27", "TW-2700", "14.90", "tableware", (198, 206, 210),
     "Reactive glaze, dishwasher safe."),
    ("Stoneware bowl, 15 cm", "stoneware-bowl-15", "TW-1500", "11.90", "tableware", (176, 190, 196),
     "Reactive glaze, dishwasher safe."),
]

DESCRIPTION = (
    "<p>Our apron is made of heavy washed linen that gets softer with every wash. The neck strap is adjustable, the "
    "long ties go round the waist and tie at the front.</p><ul><li>100% linen, 230 g/m²</li><li>Two front pockets"
    "</li><li>Machine washable at 40 °C</li></ul>"
)


def product_image(colour: tuple[int, int, int]) -> ContentFile:
    """Return a 600 × 600 JPEG in ``colour`` with a lighter square, as a stand-in for a product photo."""
    image = PILImage.new("RGB", (600, 600), colour)
    lighter = tuple(min(255, c + 40) for c in colour)
    ImageDraw.Draw(image).rounded_rectangle((150, 150, 450, 450), radius=40, fill=lighter)
    data = BytesIO()
    image.save(data, "JPEG", quality=85)
    return ContentFile(data.getvalue())


def create_demo_data() -> None:
    """Create the shop, its categories and products, and the user who logs in to take the screenshots."""
    call_command("migrate", verbosity=0)
    call_command("lfs_init")
    germany = Country.objects.create(code="de", name="Germany")
    austria = Country.objects.create(code="at", name="Austria")
    shop = Shop.objects.get()
    shop.name = "Kitchen & Table"
    shop.shop_owner = "Kitchen & Table GmbH"
    shop.from_email = "shop@example.com"
    shop.notification_emails = "orders@example.com"
    shop.default_country = germany
    shop.save()
    shop.invoice_countries.set([germany, austria])
    shop.shipping_countries.set([germany, austria])
    User.objects.create_superuser("admin", "admin@example.com", PASSWORD)

    tax = Tax.objects.create(rate=Decimal("19"), description="VAT 19%")
    ShippingMethod.objects.filter(name="Standard").update(
        tax=tax, price=Decimal("4.90"), description="<p>DHL parcel, 1–2 working days</p>"
    )
    colour = Property.objects.create(name="Colour", title="Colour", type=PROPERTY_SELECT_FIELD, filterable=True)
    for position, option in enumerate(["Sage", "Charcoal", "Natural"]):
        PropertyOption.objects.create(property=colour, name=option, position=(position + 1) * 10)
    Page.objects.filter(slug="imprint").update(
        short_text="Who runs this shop.",
        body="<p>Kitchen &amp; Table GmbH<br>Example Street 1<br>12345 Example Town</p>",
    )
    PaymentMethod.objects.filter(name="Prepayment").update(
        description="<p>Pay by bank transfer; we ship when the money has arrived.</p>"
    )
    manufacturer = Manufacturer.objects.create(name="Nordlein", slug="nordlein")
    categories = {}
    for position, (name, slug) in enumerate(CATEGORIES):
        categories[slug] = Category.objects.create(
            name=name, slug=slug, position=(position + 1) * 10, description=f"<p>{name} for every day.</p>"
        )
    for name, slug, sku, price, category, colour, short in PRODUCTS:
        product = Product.objects.create(
            name=name, slug=slug, sku=sku, price=Decimal(price), tax=tax, active=True, manufacturer=manufacturer,
            sku_manufacturer=f"NL-{sku}", short_description=f"<p>{short}</p>",
            description=DESCRIPTION if slug == "linen-apron-sage" else f"<p>{short}</p>",
        )
        product.categories.add(categories[category])
        image = Image(content=product, title=name, position=10)
        image.image.save(f"{slug}.jpg", product_image(colour), save=True)
    create_customers_and_orders(germany, tax)
    for position, slug in enumerate(["chefs-knife-20", "linen-apron-sage"]):
        FeaturedProduct.objects.create(product=Product.objects.get(slug=slug), position=(position + 1) * 10)
    Discount.objects.create(name="Autumn sale", value=10, type=DISCOUNT_TYPE_PERCENTAGE, active=True, sums_up=True)


# first name, last name, e-mail, city, order state, products with amounts
CUSTOMERS = [
    ("Anna", "Becker", "anna.becker@example.com", "Hamburg", SUBMITTED,
     [("linen-apron-sage", 1), ("tea-towel-set", 2)]),
    ("Jonas", "Weber", "jonas.weber@example.com", "Leipzig", PAID, [("bread-knife-21", 1)]),
    ("Lena", "Hoffmann", "lena.hoffmann@example.com", "Freiburg", SENT,
     [("stoneware-plate-27", 6), ("stoneware-bowl-15", 6)]),
]


def create_customers_and_orders(country: Country, tax: Tax) -> None:
    """Create registered customers with an address and an order each, an open cart, and a product review."""
    shipping = ShippingMethod.objects.get(name="Standard")
    payment = PaymentMethod.objects.get(name="Prepayment")
    address_type = ContentType.objects.get_for_model(Address)
    for number, (first, last, email, city, state, items) in enumerate(CUSTOMERS, start=1):
        user = User.objects.create_user(email.split("@")[0], email, PASSWORD, first_name=first, last_name=last)
        customer = Customer.objects.create(user=user, session=f"session-{number}")
        address = Address.objects.create(
            customer=customer, firstname=first, lastname=last, line1=f"Example Street {number}", city=city,
            zip_code=f"2{number}000", country=country, email=email,
        )
        customer.sa_content_type = customer.ia_content_type = address_type
        customer.sa_object_id = customer.ia_object_id = address.id
        customer.save()
        products = [(Product.objects.get(slug=slug), amount) for slug, amount in items]
        price = sum(product.price * amount for product, amount in products) + shipping.price
        order = Order.objects.create(
            number=f"2026-{number:05d}", user=user, session=customer.session, customer_firstname=first,
            customer_lastname=last, customer_email=email, shipping_method=shipping, payment_method=payment,
            shipping_price=shipping.price, price=price, tax=round(price * 19 / 119, 2), state=state, sa_content_type=address_type, sa_object_id=address.id,
            ia_content_type=address_type, ia_object_id=address.id,
        )
        for product, amount in products:
            OrderItem.objects.create(
                order=order, product=product, product_name=product.name, product_sku=product.sku,
                product_amount=amount, product_price_gross=product.price, price_gross=product.price * amount,
                product_tax=round(product.price * amount * 19 / 119, 2),
            )
    cart = Cart.objects.create(session="session-open-cart")
    CartItem.objects.create(cart=cart, product=Product.objects.get(slug="chefs-knife-20"), amount=1)
    CartItem.objects.create(cart=cart, product=Product.objects.get(slug="linen-apron-charcoal"), amount=2)
    Review.objects.create(
        content_type=ContentType.objects.get_for_model(Product), content_id=Product.objects.get(slug="bread-knife-21").id,
        user_name="Jonas", user_email="jonas.weber@example.com", score=5, active=False,
        comment="Cuts even the crustiest sourdough without crumbs.",
    )


class QuietHandler(WSGIRequestHandler):
    """Request handler that does not log every request."""

    def log_message(self, format: str, *args: object) -> None:
        """Drop the access log line."""


def serve_shop() -> str:
    """Serve the shop with its static and uploaded files in a background thread; return its base URL."""
    server: WSGIServer = make_server(
        "127.0.0.1", 0, StaticFilesHandler(get_wsgi_application()), handler_class=QuietHandler
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_port}"


def product_id(slug: str) -> int:
    """Return the id of the demo product ``slug``."""
    return Product.objects.get(slug=slug).id


def category_id(slug: str) -> int:
    """Return the id of the demo category ``slug``."""
    return Category.objects.get(slug=slug).id


# File name in docs/images/ (without .png) and a function that returns the path to show.
SHOTS: list[tuple[str, Callable[[], str]]] = [
    ("manage_product_data", lambda: f"/manage/product/{product_id('linen-apron-sage')}/data/"),
    ("manage_product_images", lambda: f"/manage/product/{product_id('linen-apron-sage')}/images/"),
    ("manage_product_stock", lambda: f"/manage/product/{product_id('linen-apron-sage')}/stock/"),
    ("manage_category_data", lambda: f"/manage/category/{category_id('kitchen-textiles')}/data"),
    ("manage_category_view", lambda: f"/manage/category/{category_id('kitchen-textiles')}/view/"),
    ("manage_category_products", lambda: f"/manage/category/{category_id('kitchen-textiles')}/products/"),
    ("manage_shop_data", lambda: "/manage/shop/data/"),
    ("manage_shop_default_values", lambda: "/manage/shop/default-values/"),
    ("manage_shipping_method_data", lambda: f"/manage/shipping-method/{ShippingMethod.objects.get(name='Standard').id}/data"),
    ("manage_property_data", lambda: f"/manage/property/{Property.objects.get(name='Colour').id}/data"),
    ("manage_page_data", lambda: f"/manage/page/{Page.objects.get(slug='imprint').id}/data"),
    ("manage_orders", lambda: "/manage/orders/"),
    ("manage_customers", lambda: "/manage/customers/"),
    ("manage_review", lambda: f"/manage/review/{Review.objects.get().id}/"),
    ("manage_featured", lambda: "/manage/featured"),
    ("manage_discount_data", lambda: f"/manage/discount/{Discount.objects.get().id}/data"),
    ("manage_payment_method_data", lambda: f"/manage/payment-method/{PaymentMethod.objects.get(name='Prepayment').id}/data"),
]


def take_screenshots(base: str, only: list[str]) -> None:
    """Log in and save the screenshots named in ``only`` (all when empty) at 1280 × 800 pixels."""
    from playwright.sync_api import sync_playwright

    client = Client()
    client.login(username="admin", password=PASSWORD)
    session = client.cookies["sessionid"].value
    # Look the paths up before the browser starts: Playwright runs an event loop, in which Django refuses queries.
    paths = [(name, url()) for name, url in SHOTS if not only or name in only]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.context.add_cookies([{"name": "sessionid", "value": session, "url": base}])
        for name, url in paths:
            response = page.goto(base + url)
            page.wait_for_load_state("networkidle")
            if response is None or response.status != 200:
                raise SystemExit(f"{name}: {url} answered {response.status if response else 'nothing'}")
            # The product list scrolls to the selected product; show every list from its top.
            page.evaluate("document.querySelectorAll('*').forEach(e => { e.scrollTop = 0; })")
            page.screenshot(path=IMAGES / f"{name}.png", animations="disabled")
            print(f"docs/images/{name}.png")
        browser.close()


if __name__ == "__main__":
    create_demo_data()
    take_screenshots(serve_shop(), sys.argv[1:])
