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
from django.contrib.staticfiles.handlers import StaticFilesHandler  # noqa: E402
from django.core.files.base import ContentFile  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.core.wsgi import get_wsgi_application  # noqa: E402
from django.test import Client  # noqa: E402
from PIL import Image as PILImage  # noqa: E402
from PIL import ImageDraw  # noqa: E402

from lfs.catalog.models import Category, Image, Product  # noqa: E402
from lfs.core.models import Shop  # noqa: E402
from lfs.manufacturer.models import Manufacturer  # noqa: E402
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
    shop = Shop.objects.get()
    shop.name = "Kitchen & Table"
    shop.save()
    User.objects.create_superuser("admin", "admin@example.com", PASSWORD)

    tax = Tax.objects.create(rate=Decimal("19"), description="VAT 19%")
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
