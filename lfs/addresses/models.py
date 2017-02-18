# django imports
from django.db import models
from django.db.models import SET_NULL
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.core.models import Country
from lfs.customer.models import Customer
from lfs.order.models import Order


class BaseAddress(models.Model):
    """
    Base class from which LFS addresses should inherit.

    **Attributes:**

    values_before_postal
        List of attributes which are supposed to be displayed before the postal
        form values. If the attribute ends with a ``+`` there will be no <div>
        around the value.

    values_before_postal
        List of attributes which are supposed to be displayed after the postal
        form values. If the attribute ends with a ``+`` there will be no <div>
        around the value.

    customer
        The customer the address belongs to

    order
        The order the address belongs to.

    """
    values_before_postal = None
    values_after_postal = None

    customer = models.ForeignKey(Customer, verbose_name=_(u"Customer"), blank=True, null=True, related_name="addresses",
                                 on_delete=SET_NULL)
    order = models.ForeignKey(Order, verbose_name=_(u"Order"), blank=True, null=True, related_name="addresses")

    firstname = models.CharField(_("Firstname"), max_length=50)
    lastname = models.CharField(_("Lastname"), max_length=50)
    line1 = models.CharField(_("Line 1"), max_length=100, blank=True, null=True)
    line2 = models.CharField(_("Line 2"), max_length=100, blank=True, null=True)
    zip_code = models.CharField(_("Zip code"), max_length=10, default=u"")
    city = models.CharField(_("City"), max_length=50)
    state = models.CharField(_("State"), max_length=50, blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_("Country"), blank=True, null=True)
    created = models.DateTimeField(_(u"Created"), auto_now_add=True)
    modified = models.DateTimeField(_(u"Modified"), auto_now=True)

    def get_values_before_postal(self, attributes="values_before_postal"):
        """
        Returns the values which are supposed to be displayed before the postal
        form values.
        """
        return self._get_values(attributes="values_before_postal")

    def get_values_after_postal(self):
        """
        Returns the values which are supposed to be displayed before the postal
        form values.
        """
        return self._get_values(attributes="values_after_postal")

    def as_html(self, request=None, type=None):
        """
        Returns the address as html.
        """
        templates = ["lfs/addresses/address_view.html"]
        if type:
            templates.insert(0, "lfs/addresses/%s_address_view.html" % type)

        if request:
            return render_to_string(templates, request=request, context={
                "address": self,
            })
        else:
            return render_to_string(templates, request=request, context={
                "address": self,
            })

    def _get_values(self, attributes):
        if getattr(self, attributes) is None:
            return []

        values = []
        for attribute in getattr(self, attributes):
            if attribute.endswith("+"):
                attribute = attribute[:-1]
                div = False
            else:
                div = True
            value = getattr(self, attribute)
            if value:
                values.append({
                    "value": value,
                    "div": div,
                    "attribute": attribute
                })
        return values


class Address(BaseAddress):
    """
    The default address of LFS which is used as invoice and shipping address.

    This can be replaced by an own model.
    """
    values_before_postal = ("firstname+", "lastname+", "company_name")
    values_after_postal = ("phone", "email")

    company_name = models.CharField(_("Company name"), max_length=50, blank=True, null=True)
    phone = models.CharField(_("Phone"), blank=True, null=True, max_length=20)
    email = models.EmailField(_("E-Mail"), blank=True, null=True)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.firstname, self.lastname, self.company_name)
