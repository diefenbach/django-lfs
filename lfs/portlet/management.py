# django imports
from django.db.models.signals import post_syncdb

# lfs imports
from models import AverageRatingPortlet
from models import CartPortlet
from models import CategoriesPortlet
from models import DeliveryTimePortlet
from models import FilterPortlet
from models import PagesPortlet
from models import RecentProductsPortlet
from models import RelatedProductsPortlet
from models import TextPortlet
from models import TopsellerPortlet

# 3rd party imports
import portlets
from portlets.utils import register_portlet


def register_lfs_portlets(sender, **kwargs):
    # don't register our portlets until the table has been created by syncdb
    if sender == portlets.models:
        register_portlet(AverageRatingPortlet, "Average Rating")
        register_portlet(CartPortlet, "Cart")
        register_portlet(CategoriesPortlet, "Categories")
        register_portlet(DeliveryTimePortlet, "Delivery Time")
        register_portlet(FilterPortlet, "Filter")
        register_portlet(PagesPortlet, "Pages")
        register_portlet(RecentProductsPortlet, "Recent Products")
        register_portlet(RelatedProductsPortlet, "Related Products")
        register_portlet(TextPortlet, "Text")
        register_portlet(TopsellerPortlet, "Topseller")

post_syncdb.connect(register_lfs_portlets)
