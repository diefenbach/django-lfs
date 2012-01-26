# django imports
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.template.loader import render_to_string

# lfs imports
import lfs.core.utils
from lfs import shipping
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop, Country
from lfs.criteria.models.criteria_objects import CriteriaObjects
from lfs.criteria.settings import EQUAL
from lfs.criteria.settings import LESS_THAN
from lfs.criteria.settings import LESS_THAN_EQUAL
from lfs.criteria.settings import GREATER_THAN
from lfs.criteria.settings import GREATER_THAN_EQUAL
from lfs.criteria.settings import NUMBER_OPERATORS
from lfs.criteria.settings import SELECT_OPERATORS
from lfs.criteria.settings import IS, IS_NOT, IS_VALID, IS_NOT_VALID
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod


class Criterion(object):
    """Base class for all lfs criteria.
    """
    class Meta:
        app_label = "criteria"

    def as_html(self, request, position):
        """Renders the criterion as html in order to displayed it within several
        forms.
        """
        template = "manage/criteria/%s_criterion.html" % self.content_type

        return render_to_string(template, RequestContext(request, {
            "id": "ex%s" % self.id,
            "operator": self.operator,
            "value": self.value,
            "position": position,
        }))


class CartPriceCriterion(models.Model, Criterion):
    """A criterion for the cart price.
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=NUMBER_OPERATORS)
    price = models.FloatField(_(u"Price"), default=0.0)

    def __unicode__(self):
        return _("Cart Price %(operator)s %(price)s") % {'operator': self.get_operator_display(), 'price': self.price}

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
        if product is not None:
            cart_price = product.get_price(request)
        else:
            from lfs.cart import utils as cart_utils
            cart = cart_utils.get_cart(request)

            if cart is None:
                return False

            cart_price = cart.get_price_gross(request)

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
            clag = (2 * product.get_width()) + (2 * product.get_height()) + product.get_length()
        else:
            from lfs.cart import utils as cart_utils
            cart = cart_utils.get_cart(request)
            if cart is None:
                return False

            cart_clag = 0
            max_width = 0
            max_length = 0
            total_height = 0
            for item in cart.get_items():
                if max_length < item.product.get_length():
                    max_length = item.product.get_length()

                if max_width < item.product.get_width():
                    max_width = item.product.get_width()

                total_height += item.product.get_height()

            clag = (2 * max_width) + (2 * total_height) + max_length

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
        for country in shop.shipping_countries.all():
            if country in self.countries.all():
                selected = True
            else:
                selected = False

            countries.append({
                "id" : country.id,
                "name": country.name,
                "selected": selected,
            })

        return render_to_string("manage/criteria/country_criterion.html", RequestContext(request, {
            "id": "ex%s" % self.id,
            "operator": self.operator,
            "value": self.value,
            "position": position,
            "countries": countries,
        }))


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
        if product is not None:
            cart_height = product.get_height()
        else:
            from lfs.cart import utils as cart_utils
            cart = cart_utils.get_cart(request)
            if cart is None:
                return False

            cart_height = 0
            for item in cart.get_items():
                cart_height += (item.product.get_height() * item.amount)

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


class LengthCriterion(models.Model, Criterion):
    """A criterion for the length.
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
        if product is not None:
            max_length = product.get_length()
        else:
            from lfs.cart import utils as cart_utils
            cart = cart_utils.get_cart(request)
            if cart is None:
                return False

            max_length = 0
            for item in cart.get_items():
                if max_length < item.product.get_length():
                    max_length = item.product.get_length()

        if self.operator == LESS_THAN and (max_length < self.length):
            return True
        if self.operator == LESS_THAN_EQUAL and (max_length <= self.length):
            return True
        if self.operator == GREATER_THAN and (max_length > self.length):
            return True
        if self.operator == GREATER_THAN_EQUAL and (max_length >= self.length):
            return True
        if self.operator == EQUAL and (max_length == self.length):
            return True

        return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.length


class PaymentMethodCriterion(models.Model, Criterion):
    """A criterion for the payment method.
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=SELECT_OPERATORS)
    payment_methods = models.ManyToManyField(PaymentMethod, verbose_name=_(u"Payment methods"))

    criteria_objects = generic.GenericRelation(CriteriaObjects,
        object_id_field="criterion_id", content_type_field="criterion_type")

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
        # see ShippingMethodCriterion for what's going on here
        import lfs.shipping.utils
        content_object = self.criteria_objects.filter()[0].content
        if isinstance(content_object, PaymentMethod):
            is_payment_method = True
        else:
            is_payment_method = False

        if not is_payment_method and self.operator == IS:
            payment_method = lfs.payment.utils.get_selected_payment_method(request)
            return payment_method in self.payment_methods.all()
        elif not is_payment_method and self.operator == IS_NOT:
            payment_method = lfs.payment.utils.get_selected_payment_method(request)
            return payment_method not in self.payment_methods.all()
        elif self.operator == IS_VALID:
            for pm in self.payment_methods.all():
                if not lfs.criteria.utils.is_valid(request, pm, product):
                    return False
            return True
        elif self.operator == IS_NOT_VALID:
            for pm in self.payment_methods.all():
                if lfs.criteria.utils.is_valid(request, pm, product):
                    return False
            return True
        else:
            return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.payment_methods

    def as_html(self, request, position):
        """Renders the criterion as html in order to be displayed within several
        forms.
        """
        selected_payment_methods = self.payment_methods.all()
        payment_methods = []
        for pm in PaymentMethod.objects.filter(active=True):
            if pm in selected_payment_methods:
                selected = True
            else:
                selected = False

            payment_methods.append({
                "id": pm.id,
                "name": pm.name,
                "selected": selected,
            })

        return render_to_string("manage/criteria/payment_method_criterion.html", RequestContext(request, {
            "id": "ex%s" % self.id,
            "operator": self.operator,
            "value": self.value,
            "position": position,
            "payment_methods": payment_methods,
        }))


class ShippingMethodCriterion(models.Model, Criterion):
    """A criterion for the shipping method.
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=SELECT_OPERATORS)
    shipping_methods = models.ManyToManyField(ShippingMethod, verbose_name=_(u"Shipping methods"))

    criteria_objects = generic.GenericRelation(CriteriaObjects,
        object_id_field="criterion_id", content_type_field="criterion_type")

    def __unicode__(self):
        values = []
        for value in self.value.all():
            values.append(value.name)

        return "%s %s %s" % ("Shipping", self.get_operator_display(), ", ".join(values))

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"shipping_method"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Shipping method")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.
        """
        # Check whether the criteria is part of a shipping method if so the
        # operator IS and IS_NOT are not allowed. This will later exluded by the
        # UID.

        # The reason why we have to check this is that the get_selected_shipping_method
        # checks for valid shipping methods and call this method again, so that
        # we get an infinte recursion.

        import lfs.shipping.utils
        content_object = self.criteria_objects.filter()[0].content
        if isinstance(content_object, ShippingMethod):
            is_shipping_method = True
        else:
            is_shipping_method = False

        if not is_shipping_method and self.operator == IS:
            shipping_method = lfs.shipping.utils.get_selected_shipping_method(request)
            return shipping_method in self.shipping_methods.all()
        elif not is_shipping_method and self.operator == IS_NOT:
            shipping_method = lfs.shipping.utils.get_selected_shipping_method(request)
            return shipping_method not in self.shipping_methods.all()
        elif self.operator == IS_VALID:
            for sm in self.shipping_methods.all():
                if not lfs.criteria.utils.is_valid(request, sm, product):
                    return False
            return True
        elif self.operator == IS_NOT_VALID:
            for sm in self.shipping_methods.all():
                if lfs.criteria.utils.is_valid(request, sm, product):
                    return False
            return True
        else:
            return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.shipping_methods

    def as_html(self, request, position):
        """Renders the criterion as html in order to be displayed within several
        forms.
        """
        selected_shipping_methods = self.shipping_methods.all()
        shipping_methods = []
        for sm in ShippingMethod.objects.filter(active=True):
            if sm in selected_shipping_methods:
                selected = True
            else:
                selected = False

            shipping_methods.append({
                "id": sm.id,
                "name": sm.name,
                "selected": selected,
            })

        return render_to_string("manage/criteria/shipping_method_criterion.html", RequestContext(request, {
            "id": "ex%s" % self.id,
            "operator": self.operator,
            "value": self.value,
            "position": position,
            "shipping_methods": shipping_methods,
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
            cart_weight = product.get_weight()
        else:
            from lfs.cart import utils as cart_utils
            cart = cart_utils.get_cart(request)

            if cart is None:
                return False

            cart_weight = 0
            for item in cart.get_items():
                cart_weight += (item.product.get_weight() * item.amount)

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
        if product is not None:
            max_width = product.get_width()
        else:
            from lfs.cart import utils as cart_utils
            cart = cart_utils.get_cart(request)
            if cart is None:
                return False

            max_width = 0
            for item in cart.get_items():
                if max_width < item.product.get_width():
                    max_width = item.product.get_width()

        if self.operator == LESS_THAN and (max_width < self.width):
            return True
        if self.operator == LESS_THAN_EQUAL and (max_width <= self.width):
            return True
        if self.operator == GREATER_THAN and (max_width > self.width):
            return True
        if self.operator == GREATER_THAN_EQUAL and (max_width >= self.width):
            return True
        if self.operator == EQUAL and (max_width == self.width):
            return True

        return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.width


class DistanceCriterion(models.Model, Criterion):
    """
    """
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True, choices=NUMBER_OPERATORS)
    distance = models.FloatField(_(u"Distance"), default=0.0)
    module = models.CharField(blank=True, max_length=100)

    def __unicode__(self):
        return "Distance: %s %s" % (self.get_operator_display(), self.distance)

    @property
    def content_type(self):
        """Returns the content_type of the criterion as lower string.

        This is for instance used to select the appropriate form for the
        criterion.
        """
        return u"distance"

    @property
    def name(self):
        """Returns the descriptive name of the criterion.
        """
        return _(u"Distance")

    def is_valid(self, request, product=None):
        """Returns True if the criterion is valid.
        """
        try:
            m = lfs.core.utils.import_module(settings.LFS_DISTANCE_MODULE)
            current_distance = m.get_distance(request)
        except (ImportError, AttributeError):
            current_distance = 0

        if self.operator == LESS_THAN and (current_distance < self.distance):
            return True
        if self.operator == LESS_THAN_EQUAL and (current_distance <= self.distance):
            return True
        if self.operator == GREATER_THAN and (current_distance > self.distance):
            return True
        if self.operator == GREATER_THAN_EQUAL and (current_distance >= self.distance):
            return True
        if self.operator == EQUAL and (current_distance == self.distance):
            return True

        return False

    @property
    def value(self):
        """Returns the value of the criterion.
        """
        return self.distance
