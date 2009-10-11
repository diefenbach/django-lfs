# django imports
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.template.loader import render_to_string

# lfs imports
from lfs import shipping
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Country
from lfs.core.models import Shop
from lfs.criteria.settings import EQUAL
from lfs.criteria.settings import LESS_THAN
from lfs.criteria.settings import LESS_THAN_EQUAL
from lfs.criteria.settings import GREATER_THAN
from lfs.criteria.settings import GREATER_THAN_EQUAL
from lfs.criteria.settings import NUMBER_OPERATORS
from lfs.criteria.settings import SELECT_OPERATORS, IS
from lfs.payment.models import PaymentMethod

class Criterion(object):
    """Base class for all lfs criteria.
    """
    def as_html(self, request, position):
        """Renders the criterion as html in order to displayed it within several
        forms.
        """
        template = "manage/criteria/%s_criterion.html" % self.content_type

        return render_to_string(template, RequestContext(request, {
            "id" : "ex%s" % self.id,
            "operator" : self.operator,
            "value" : self.value,
            "position" : position,
        }))

class CombinedLengthAndGirthCriterion(models.Model, Criterion):
    """A criterion for the combined length and girth.
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=NUMBER_OPERATORS)
    clag = models.FloatField(_(u"Width"), default=0.0)

    def __unicode__(self):
        return "CLAG: %s %s" % (self.get_operator_display(), self.clag)

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"combinedlengthandgirth"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Combined length and girth")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.

        If product is given the combined length and girth is taken from the
        product otherwise from the cart.
        """
        if product is not None:
            clag = (2 * product.width) + (2 * product.height) + product.length
        else:
            from lfs.cart import utils as cart_utils
            cart = cart_utils.get_cart(request)
            if cart is None:
                return False

            cart_clag = 0
            max_width = 0
            max_length = 0
            total_height = 0
            for item in cart.items():
                if max_length < item.product.length:
                    max_length = item.product.length

                if max_width < item.product.width:
                    max_width = item.product.width

                total_height += item.product.height

            clag = (2 * max_width) +  (2 * total_height) + max_length

        if self.operator == LESS_THAN and (clag < self.clag):
            return True
        if self.operator == LESS_THAN_EQUAL and (clag <= self.clag):
            return True
        if self.operator == GREATER_THAN and (clag > self.clag):
            return True
        if self.operator == GREATER_THAN_EQUAL and (clag >= self.clag):
            return True
        if self.operator == EQUAL and (clag == self.clag):
            return True

        return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.clag

class CountryCriterion(models.Model, Criterion):
    """A criterion for the shipping country.
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=SELECT_OPERATORS)
    countries = models.ManyToManyField(Country, verbose_name=_(u"Countries"))

    def __unicode__(self):
        values = []
        for value in self.value.all():
            values.append(value.name)

        return "%s %s %s" % ("Country", self.get_operator_display(), ", ".join(values))

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"country"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Country")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.
        """
        country = shipping.utils.get_selected_shipping_country(request)
        if self.operator == IS:
            return country in self.countries.all()
        else:
            return country not in self.countries.all()

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.countries

    def as_html(self, request, position):
        """Renders the criterion as html in order to be displayed within several
        forms.
        """
        shop = lfs_get_object_or_404(Shop, pk=1)

        countries = []
        for country in shop.countries.all():
            if country in self.countries.all():
                selected = True
            else:
                selected = False

            countries.append({
                "id" : country.id,
                "name" : country.name,
                "selected" : selected,
            })

        return render_to_string("manage/criteria/country_criterion.html", RequestContext(request, {
            "id" : "ex%s" % self.id,
            "operator" : self.operator,
            "value" : self.value,
            "position" : position,
            "countries" : countries,
        }))

class PaymentMethodCriterion(models.Model, Criterion):
    """A criterion for the payment method.
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=SELECT_OPERATORS)
    # payment_methods = models.ManyToManyField(PaymentMethod, verbose_name=_(u"Payment methods"))

    def __unicode__(self):
        values = []
        for value in self.value.all():
            values.append(value.name)

        return "%s %s %s" % ("Payment", self.get_operator_display(), ", ".join(values))

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"payment_method"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Payment method")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.
        """
        payment_method = lfs.payment.utils.get_selected_payment_method(request)
        if self.operator == IS:
            return payment_method in self.payment_methods.all()
        else:
            return payment_method not in self.payment_methods.all()

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.countries

    def as_html(self, request, position):
        """Renders the criterion as html in order to be displayed within several
        forms.
        """
        shop = lfs_get_object_or_404(Shop, pk=1)

        countries = []
        for country in shop.countries.all():
            if country in self.countries.all():
                selected = True
            else:
                selected = False

            countries.append({
                "id" : country.id,
                "name" : country.name,
                "selected" : selected,
            })

        return render_to_string("manage/criteria/country_criterion.html", RequestContext(request, {
            "id" : "ex%s" % self.id,
            "operator" : self.operator,
            "value" : self.value,
            "position" : position,
            "countries" : countries,
        }))

class UserCriterion(models.Model, Criterion):
    """A criterion for user content objects
    """
    users = models.ManyToManyField(User)

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"user"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"User")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.
        """
        return request.user in self.users.all()

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.users

class CartPriceCriterion(models.Model, Criterion):
    """A criterion for the cart price.
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=NUMBER_OPERATORS)
    price = models.FloatField(_(u"Price"), default=0.0)

    def __unicode__(self):
        return "Cart Price %s %s" % (self.get_operator_display(), self.price)

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"price"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Cart Price")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.

        If product is given the price is taken from the product otherwise from
        the cart.
        """
        from lfs.cart import utils as cart_utils
        cart = cart_utils.get_cart(request)

        if cart is None:
            return False

        if product is not None:
            cart_price = product.get_price()
        else:
            cart_price = cart_utils.get_cart_price(request, cart)

        if self.operator == LESS_THAN and (cart_price < self.price):
            return True
        if self.operator == LESS_THAN_EQUAL and (cart_price <= self.price):
            return True
        if self.operator == GREATER_THAN and (cart_price > self.price):
            return True
        if self.operator == GREATER_THAN_EQUAL and (cart_price >= self.price):
            return True
        if self.operator == EQUAL and (cart_price == self.price):
            return True

        return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.price

class WeightCriterion(models.Model, Criterion):
    """
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=NUMBER_OPERATORS)
    weight = models.FloatField(_(u"Weight"), default=0.0)

    def __unicode__(self):
        return "Weight: %s %s" % (self.get_operator_display(), self.weight)

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"weight"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Weight")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.

        If product is given the weight is taken from the product otherwise from
        the cart.
        """
        if product is not None:
            cart_weight = product.weight
        else:
            from lfs.cart import utils as cart_utils
            cart = cart_utils.get_cart(request)

            if cart is None:
                return False

            cart_weight = 0
            for item in cart.items():
                cart_weight += (item.product.weight * item.amount)

        if self.operator == LESS_THAN and (cart_weight < self.weight):
            return True
        if self.operator == LESS_THAN_EQUAL and (cart_weight <= self.weight):
            return True
        if self.operator == GREATER_THAN and (cart_weight > self.weight):
            return True
        if self.operator == GREATER_THAN_EQUAL and (cart_weight >= self.weight):
            return True
        if self.operator == EQUAL and (cart_weight == self.weight):
            return True

        return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.weight

class HeightCriterion(models.Model, Criterion):
    """
    """
    operator = models.PositiveIntegerField(blank=True, null=True, choices=NUMBER_OPERATORS)
    height = models.FloatField(_(u"Height"), default=0.0)

    def __unicode__(self):
        return "Height: %s %s" % (self.get_operator_display(), self.height)

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"height"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Height")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.

        If product is given the height is taken from the product otherwise from
        the cart.
        """
        from lfs.cart import utils as cart_utils
        cart = cart_utils.get_cart(request)
        if cart is None:
            return False

        if product is not None:
            cart_height = product.height
        else:
            cart_height = 0
            for item in cart.items():
                cart_height += (item.product.height * item.amount)

        if self.operator == LESS_THAN and (cart_height < self.height):
            return True
        if self.operator == LESS_THAN_EQUAL and (cart_height <= self.height):
            return True
        if self.operator == GREATER_THAN and (cart_height > self.height):
            return True
        if self.operator == GREATER_THAN_EQUAL and (cart_height >= self.height):
            return True
        if self.operator == EQUAL and (cart_height == self.height):
            return True

        return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.height

class WidthCriterion(models.Model, Criterion):
    """
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=NUMBER_OPERATORS)
    width = models.FloatField(_(u"Width"), default=0.0)

    def __unicode__(self):
        return "Width: %s %s" % (self.get_operator_display(), self.width)

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"width"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Height")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.

        If product is given the width is taken from the product otherwise from
        the cart.
        """
        from lfs.cart import utils as cart_utils
        cart = cart_utils.get_cart(request)
        if cart is None:
            return False

        if product is not None:
            cart_width = product.width
        else:
            cart_width = 0
            for item in cart.items():
                cart_width += (item.product.width * item.amount)

        if self.operator == LESS_THAN and (cart_width < self.width):
            return True
        if self.operator == LESS_THAN_EQUAL and (cart_width <= self.width):
            return True
        if self.operator == GREATER_THAN and (cart_width > self.width):
            return True
        if self.operator == GREATER_THAN_EQUAL and (cart_width >= self.width):
            return True
        if self.operator == EQUAL and (cart_width == self.width):
            return True

        return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.width

class LengthCriterion(models.Model, Criterion):
    """
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=NUMBER_OPERATORS)
    length = models.FloatField(_(u"Length"), default=0.0)

    def __unicode__(self):
        return "Length: %s %s" % (self.get_operator_display(), self.length)

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"length"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Length")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.

        If product is given the length is taken from the product otherwise from
        the cart.
        """
        from lfs.cart import utils as cart_utils
        cart = cart_utils.get_cart(request)
        if cart is None:
            return False

        if product is not None:
            cart_length = product.length
        else:
            cart_length = 0
            for item in cart.items():
                cart_length += (item.product.length * item.amount)

        if self.operator == LESS_THAN and (cart_length < self.length):
            return True
        if self.operator == LESS_THAN_EQUAL and (cart_length <= self.length):
            return True
        if self.operator == GREATER_THAN and (cart_length > self.length):
            return True
        if self.operator == GREATER_THAN_EQUAL and (cart_length >= self.length):
            return True
        if self.operator == EQUAL and (cart_length == self.length):
            return True

        return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.length

class CriteriaObjects(models.Model):
    """Assigns arbitrary criteria to arbitrary content objects.
    """
    class Meta:
        ordering = ["position"]
        verbose_name_plural = "Criteria objects"

    criterion_type = models.ForeignKey(ContentType, verbose_name=_(u"Criterion type"), related_name="criterion")
    criterion_id = models.PositiveIntegerField(_(u"Content id"))
    criterion = generic.GenericForeignKey(ct_field="criterion_type", fk_field="criterion_id")

    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name="content_type")
    content_id = models.PositiveIntegerField(_(u"Content id"))
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")

    position = models.PositiveIntegerField(_(u"Position"), default=999)
