# django imports
from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

# portlets imports
import portlets.utils
from portlets.models import Slot

# lfs import
import lfs.core.utils
from lfs.portlet.models import CartPortlet
from lfs.portlet.models import CategoriesPortlet
from lfs.portlet.models import PagesPortlet
from lfs.portlet.models import RecentProductsPortlet
from lfs.portlet.models import RelatedProductsPortlet
from lfs.portlet.models import TopsellerPortlet

register = template.Library()


# TODO: Make a better reuse of django-portlets portlet slot
@register.inclusion_tag('portlets/portlet_slot.html', takes_context=True)
def lfs_portlet_slot(context, slot_name):
    """Returns the portlets for given slot and instance. If the instance
    implements the ``get_parent_for_portlets`` method the portlets of the
    parent of the instance are also added.
    """
    instance = context.get("category") or \
               context.get("product") or \
               lfs.core.utils.get_default_shop()

    cache_key = "%s-lfs-portlet-slot-%s-%s-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, slot_name, instance.__class__.__name__, instance.id)
    temp = cache.get(cache_key)

    if temp is None:
        try:
            slot = Slot.objects.get(name=slot_name)
        except Slot.DoesNotExist:
            return {"portlets": []}

        # Get portlets for given instance
        temp = portlets.utils.get_portlets(instance, slot)

        # Get inherited portlets
        try:
            instance.get_parent_for_portlets()
        except AttributeError:
            instance = None

        while instance:
            # If the portlets are blocked no portlets should be added
            if portlets.utils.is_blocked(instance, slot):
                break

            # If the instance has no get_parent_for_portlets, there are no portlets
            try:
                instance = instance.get_parent_for_portlets()
            except AttributeError:
                break

            # If there is no parent for portlets, there are no portlets to add
            if instance is None:
                break

            parent_portlets = portlets.utils.get_portlets(instance, slot)
            parent_portlets.reverse()
            for p in parent_portlets:
                if p not in temp:
                    temp.insert(0, p)

            cache.set(cache_key, temp)

    rendered_portlets = []
    for portlet in temp:
        rendered_portlets.append(portlet.render(context))

    return {"portlets": rendered_portlets}


# Inclusion tags to render portlets. This can be used if one wants to display
# portlets without the possibility to manage them via the UI.
@register.inclusion_tag('lfs/portlets/portlet.html', takes_context=True)
def lfs_cart_portlet(context, title=None):
    """Tag to render the cart portlet.
    """
    if title is None:
        title = _(u"Cart")

    portlet = CartPortlet()
    portlet.title = title

    return {
        "html": portlet.render(context)
    }


@register.inclusion_tag('lfs/portlets/portlet.html', takes_context=True)
def lfs_categories_portlet(context, title=None):
    """Tag to render the related products portlet.
    """
    if title is None:
        title = _(u"Categories")

    portlet = CategoriesPortlet()
    portlet.title = title

    return {
        "html": portlet.render(context)
    }


@register.inclusion_tag('lfs/portlets/portlet.html', takes_context=True)
def lfs_pages_portlet(context, title=None):
    """Tag to render the pages portlet.
    """
    if title is None:
        title = _(u"Information")

    portlet = PagesPortlet()
    portlet.title = title

    return {
        "html": portlet.render(context)
    }


@register.inclusion_tag('lfs/portlets/portlet.html', takes_context=True)
def lfs_recent_products_portlet(context, title=None):
    """Tag to render the recent products portlet.
    """
    if title is None:
        title = _(u"Recent Products")

    portlet = RecentProductsPortlet()
    portlet.title = title

    return {
        "html": portlet.render(context)
    }


@register.inclusion_tag('lfs/portlets/portlet.html', takes_context=True)
def lfs_related_products_portlet(context, title=None):
    """Tag to render the related products portlet.
    """
    if title is None:
        title = _(u"Related Products")

    portlet = RelatedProductsPortlet()
    portlet.title = title

    return {
        "html": portlet.render(context)
    }


@register.inclusion_tag('lfs/portlets/portlet.html', takes_context=True)
def lfs_topseller_portlet(context, title=None, limit=5):
    """Tag to render the related products portlet.
    """
    if title is None:
        title = _(u"Topseller")

    portlet = TopsellerPortlet()
    portlet.title = title
    portlet.limit = limit

    return {
        "html": portlet.render(context)
    }
