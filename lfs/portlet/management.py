from django.db.models.signals import post_migrate
from django.dispatch import receiver

from portlets.utils import register_portlet

from . models import AverageRatingPortlet
from . models import CartPortlet
from . models import CategoriesPortlet
from . models import DeliveryTimePortlet
from . models import FilterPortlet
from . models import PagesPortlet
from . models import RecentProductsPortlet
from . models import RelatedProductsPortlet
from . models import TextPortlet
from . models import TopsellerPortlet
from . models import ForsalePortlet
from . models import FeaturedPortlet
from . models import LatestPortlet


@receiver(post_migrate)
def register_lfs_portlets(sender, **kwargs):
    if sender.name == "portlets":
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
        register_portlet(ForsalePortlet, "For sale")
        register_portlet(FeaturedPortlet, "Featured Products")
        register_portlet(LatestPortlet, "Latest Products")
