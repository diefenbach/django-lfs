"""The cached product page must not hand one visitor's CSRF token to the next visitor."""

import re

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from lfs.cart.models import CartItem
from lfs.catalog.models import Product

LOCMEM_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "csrf-test"}}
TOKEN_RE = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')


@override_settings(CACHES=LOCMEM_CACHE)
class CachedProductPageCsrfTestCase(TestCase):
    fixtures = ["lfs_shop.xml"]

    def setUp(self):
        self.product = Product.objects.create(name="Product 1", slug="product-1", active=True, price=10)
        self.url = reverse("lfs_product", kwargs={"slug": self.product.slug})

    def test_second_visitor_can_add_to_cart_from_cached_product_page(self):
        first = Client(enforce_csrf_checks=True)
        first_page = first.get(self.url).content.decode()
        self.assertIsNotNone(TOKEN_RE.search(first_page), "the product page must contain the add-to-cart form")

        # The second visitor gets the product inline from the cache.
        second = Client(enforce_csrf_checks=True)
        second_page = second.get(self.url).content.decode()
        token = TOKEN_RE.search(second_page).group(1)

        response = second.post(
            reverse("lfs_product_dispatcher"),
            {"csrfmiddlewaretoken": token, "action": "add-to-cart", "product_id": self.product.id, "quantity": "1"},
        )

        self.assertNotEqual(response.status_code, 403)
        self.assertTrue(
            CartItem.objects.filter(cart__session=second.session.session_key, product=self.product).exists()
        )
