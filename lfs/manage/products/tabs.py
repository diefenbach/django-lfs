"""Tabs that add-ons add to the product management page.

An add-on registers its tab in its ``AppConfig.ready()`` and provides the view (a ``ProductTabMixin`` view with
``tab_name`` set to the tab's key), its URL, and the template with the tab's content::

    register_product_tab(ProductTab(
        key="bulk_prices",
        label=_("Bulk prices"),
        url_name="lfs_manage_product_bulk_prices",
        template="lfs_bulk_prices/manage/tab.html",
        show=lambda request, product: isinstance(product.get_price_calculator(request), BulkPricesCalculator),
    ))
"""

from dataclasses import dataclass
from typing import Callable

from django.http import HttpRequest
from django.utils.functional import Promise

from lfs.catalog.models import Product


def _always(request: HttpRequest, product: Product) -> bool:
    """Show the tab for every product."""
    return True


@dataclass(frozen=True)
class ProductTab:
    """A tab of an add-on on the product management page.

    ``url_name`` is reversed with the product's id; ``show`` decides per product whether the tab is listed.
    """

    key: str
    label: str | Promise
    url_name: str
    template: str
    show: Callable[[HttpRequest, Product], bool] = _always


_tabs: dict[str, ProductTab] = {}


def register_product_tab(tab: ProductTab) -> None:
    """Add ``tab`` to the product management page; a tab with the same key is replaced."""
    _tabs[tab.key] = tab


def unregister_product_tab(key: str) -> None:
    """Remove the tab with ``key``; does nothing if there is none."""
    _tabs.pop(key, None)


def product_tabs() -> list[ProductTab]:
    """Return the registered tabs in the order they were registered."""
    return list(_tabs.values())


def get_product_tab(key: str | None) -> ProductTab | None:
    """Return the registered tab with ``key``, or None."""
    return _tabs.get(key) if key else None
