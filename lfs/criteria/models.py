from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _, ugettext
from django.template.loader import render_to_string

import lfs.cart.utils
import lfs.core.utils
from lfs import shipping
from lfs.core.models import Country
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod


class Criterion(models.Model):
    """
    Base class for all criteria.

    **Attributes:**

    cart
        The current cart of the current customer.

    content
        The content object the criterion belongs to.

    operator
        The current selected operator for the criterion.

    position
        The position of the criterion within a list of criteria of the
        content object.

    product
        The product, if the criterion is called from a product detail view.
        Otherwise this is None.

    request
        The current request.

    **Constants:**

    EQUAL, LESS_THAN, LESS_THAN_EQUAL, GREATER_THAN, GREATER_THAN_EQUAL, IS_SELECTED, IS_NOT_SELECTED, IS_VALID, IS_NOT_VALID, CONTAINS
        Integers which represents certain operators.

    INPUT, SELECT, MULTIPLE_SELECT
        Constants which represents the types of selectable values. One of
        these must be returned from ``get_value_type``.

    NUMBER_OPERATORS
        A list of operators which can be returned from ``get_operators``.

        .. code-block:: python

            [
                [EQUAL, _(u"Equal to")],
                [LESS_THAN, _(u"Less than")],
                [LESS_THAN_EQUAL, _(u"Less than equal to")],
                [GREATER_THAN, _(u"Greater than")],
                [GREATER_THAN_EQUAL, _(u"Greater than equal to")],
            ]


    SELECTION_OPERATORS
        A list of operators which can be returned from ``get_operators``.

        .. code-block:: python

            [
                [IS_SELECTED, _(u"Is selected")],
                [IS_NOT_SELECTED, _(u"Is not selected")],
            ]

    VALID_OPERATORS
        A list of operators which can be returned from ``get_operators``.

        .. code-block:: python

            [
                [IS_VALID, _(u"Is valid")],
                [IS_NOT_VALID, _(u"Is not valid")],
            ]

    STRING_OPERATORS
        A list of operators which can be return from ``get_operators``.

        .. code-block:: python

            [
                [EQUAL, _(u"Equal to")],
                [CONTAINS, _(u"Contains")],
            ]
    """
    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name="content_type")
    content_id = models.PositiveIntegerField(_(u"Content id"))
    content = GenericForeignKey(ct_field="content_type", fk_field="content_id")
    sub_type = models.CharField(_(u"Sub type"), max_length=100, blank=True)

    position = models.PositiveIntegerField(_(u"Position"), default=999)
    operator = models.PositiveIntegerField(_(u"Operator"), blank=True, null=True)

    class Meta:
        ordering = ("position", )
        app_label = 'criteria'

    EQUAL = 0
    LESS_THAN = 1
    LESS_THAN_EQUAL = 2
    GREATER_THAN = 3
    GREATER_THAN_EQUAL = 4
    IS_SELECTED = 10
    IS_NOT_SELECTED = 11
    IS_VALID = 21
    IS_NOT_VALID = 22
    CONTAINS = 32

    INPUT = 0
    SELECT = 1
    MULTIPLE_SELECT = 2

    NUMBER_OPERATORS = [
        [EQUAL, _(u"Equal to")],
        [LESS_THAN, _(u"Less than")],
        [LESS_THAN_EQUAL, _(u"Less than equal to")],
        [GREATER_THAN, _(u"Greater than")],
        [GREATER_THAN_EQUAL, _(u"Greater than equal to")],
    ]

    SELECTION_OPERATORS = [
        [IS_SELECTED, _(u"Is selected")],
        [IS_NOT_SELECTED, _(u"Is not selected")],
    ]

    VALID_OPERATORS = [
        [IS_VALID, _(u"Is valid")],
        [IS_NOT_VALID, _(u"Is not valid")],
    ]

    STRING_OPERATORS = [
        [EQUAL, _(u"Equal to")],
        [CONTAINS, _(u"Contains")],
    ]

    def __unicode__(self):
        """ We're using force unicode as this basically fails:
               from django.utils import translation
               from django.utils.translation import ugettext_lazy as _
               translation.activate('pl')
               u'test: %s' % _('Payment method')
        """
        return ugettext("%(name)s: %(operator)s %(value)s") % {
            'name': force_unicode(self.get_name()),
            'operator': force_unicode(self.get_current_operator_as_string()),
            'value': force_unicode(self.get_value_as_string())
        }

    def save(self, *args, **kwargs):
        if self.sub_type == "":
            self.sub_type = self.__class__.__name__.lower()
        super(Criterion, self).save(*args, **kwargs)

    @property
    def cart(self):
        """
        Returns the current cart of the current customer.
        """
        return lfs.cart.utils.get_cart(self.request)

    def get_content_object(self):
        """
        Returns the specific content object of the criterion.

        This can be call on Criterion instances to get the specific criterion
        instance.
        """
        if self.__class__.__name__.lower() == "criterion":
            return getattr(self, self.sub_type)
        else:
            return self

    def get_current_operator_as_string(self):
        """
        Returns the current operator as string.
        """
        for operator in self.get_operators():
            if self.operator == operator[0]:
                return operator[1]

    def get_name(self):
        """
        Returns the name of the criterion as string.
        """
        klass = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        for x in settings.LFS_CRITERIA:
            if x[0] == klass:
                return x[1]
        return self.__class__.__name__

    def get_operators(self):
        """
        Returns the selectable operators of the criterion which are displayed to
        the shop manager. This is a list of list, whereas the the first value is
        integer, which is stored within the criterion and the second value is
        the string which is displayed to the shop manager, e.g.:

        .. code-block:: python

            [
                [0, _(u"Equal to")],
                [1, _(u"Less than")],
                [2, _(u"Less than equal to")],
                [3, _(u"Greater than")],
                [4, _(u"Greater than equal to")],
            ]

        .. note::

            You can use one of the provided class attributes, see above.

            * NUMBER_OPERATORS
            * SELECTION_OPERATORS
            * VALID_OPERATORS
            * STRING_OPERATORS
        """
        raise NotImplementedError

    def get_selectable_values(self, request):
        """
        Returns the selectable values as a list of dictionary:

            [
                {
                    "id": 0,
                    "name": "Name 0",
                    "selected": False,
                },
                {
                    "id": 1,
                    "name": "Name 1",
                    "selected": True,
                },
            ]

        """
        return []

    def get_template(self, request):
        """
        Returns the template to render the criterion.
        """
        return "manage/criteria/base.html"

    def get_value(self):
        """
        Returns the current value of the criterion.
        """
        return self.value

    def get_value_type(self):
        """
        Returns the type of the selectable values field. Must return one of:

            * self.INPUT
            * self.SELECT
            * self.MULTIPLE_SELECT
        """
        return self.INPUT

    def get_value_as_string(self):
        """
        Returns the current value of the criterion as string.
        """
        value = self.get_value()

        if value.__class__.__name__ == "ManyRelatedManager":
            values = []
            for value in self.get_value().all():
                values.append(value.name)
            return ", ".join(values)
        else:
            return value

    def is_valid(self):
        """
        Returns ``True`` if the criterion is valid otherwise ``False``.
        """
        raise NotImplementedError

    def render(self, request, position):
        """
        Renders the criterion as html in order to displayed it within the
        management form.
        """
        operators = []
        for operator in self.get_operators():
            if self.operator == operator[0]:
                selected = True
            else:
                selected = False

            operators.append({
                "id": operator[0],
                "name": operator[1].encode("utf-8"),
                "selected": selected,
            })

        criteria = []
        for criterion in settings.LFS_CRITERIA:
            klass = criterion[0].split(".")[-1]
            if self.__class__.__name__ == klass:
                selected = True
            else:
                selected = False

            criteria.append({
                "module": criterion[0],
                "name": criterion[1],
                "selected": selected,
            })

        if self.id:
            id = "ex%s" % self.id
        else:
            id = timezone.now().microsecond

        return render_to_string(self.get_template(request), request=request, context={
            "id": id,
            "operator": self.operator,
            "value": self.get_value(),
            "position": position,
            "operators": operators,
            "criteria": criteria,
            "selectable_values": self.get_selectable_values(request),
            "value_type": self.get_value_type(),
            "criterion": self,
        })

    def update(self, value):
        """
        Updates the value of the criterion.

        **Parameters:**

        value
            The value the shop user has entered for the criterion.
        """
        if isinstance(self.value, float):
            try:
                value = float(value)
            except (ValueError, TypeError):
                value = 0.0
            self.value = value
        elif isinstance(self.value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                value = 0
            self.value = value
        elif self.value.__class__.__name__ == "ManyRelatedManager":
            for value_id in value:
                self.value.add(value_id)
        else:
            self.value = value

        self.save()


class CartPriceCriterion(Criterion):
    """
    Criterion to check against cart/product price.
    """
    value = models.FloatField(_(u"Price"), default=0.0)

    def get_operators(self):
        """
        Returns the available operators for the criterion.
        """
        return self.NUMBER_OPERATORS

    def is_valid(self):
        """
        If product is given, the price is taken from the product, otherwise it
        is the total price of all products within the cart.
        """
        if self.product:
            price = self.product.get_price(self.request)
        elif self.cart:
            price = self.cart.get_price_gross(self.request)
        else:
            price = 0

        if (self.operator == self.EQUAL) and (price == self.value):
            return True
        elif (self.operator == self.LESS_THAN) and (price < self.value):
            return True
        elif (self.operator == self.LESS_THAN_EQUAL) and (price <= self.value):
            return True
        elif (self.operator == self.GREATER_THAN) and (price > self.value):
            return True
        elif (self.operator == self.GREATER_THAN_EQUAL) and (price >= self.value):
            return True
        else:
            return False

    class Meta:
        app_label = 'criteria'


class CombinedLengthAndGirthCriterion(Criterion):
    """
    Criterion to check against combined length and girth.
    """
    value = models.FloatField(_(u"CLAG"), default=0.0)

    def get_operators(self):
        """
        Returns the available operators for the criterion.
        """
        return self.NUMBER_OPERATORS

    def is_valid(self):
        """
        If product is given, the clag is taken from the product, otherwise it is
        the clag of all products within the cart.
        """
        if self.product:
            clag = (2 * self.product.get_width()) + (2 * self.product.get_height()) + self.product.get_length()
        else:
            if self.cart is None:
                clag = 0
            else:
                max_width = 0
                max_length = 0
                total_height = 0
                for item in self.cart.get_items():
                    if max_length < item.product.get_length():
                        max_length = item.product.get_length()

                    if max_width < item.product.get_width():
                        max_width = item.product.get_width()

                    total_height += item.product.get_height()

                clag = (2 * max_width) + (2 * total_height) + max_length

        if (self.operator == self.EQUAL) and (clag == self.value):
            return True
        elif (self.operator == self.LESS_THAN) and (clag < self.value):
            return True
        elif (self.operator == self.LESS_THAN_EQUAL) and (clag <= self.value):
            return True
        elif (self.operator == self.GREATER_THAN) and (clag > self.value):
            return True
        elif (self.operator == self.GREATER_THAN_EQUAL) and (clag >= self.value):
            return True
        else:
            return False

    class Meta:
        app_label = 'criteria'


class CountryCriterion(Criterion):
    """
    Criterion to check against shipping country.
    """
    value = models.ManyToManyField(Country, verbose_name=_(u"Countries"))

    def get_operators(self):
        """
        Returns the available operators for the criterion.
        """
        return self.SELECTION_OPERATORS

    def get_selectable_values(self, request):
        shop = lfs.core.utils.get_default_shop(request)
        countries = []
        for country in shop.shipping_countries.all():
            if country in self.value.all():
                selected = True
            else:
                selected = False

            countries.append({
                "id": country.id,
                "name": country.name,
                "selected": selected,
            })

        return countries

    def get_value_type(self):
        return self.MULTIPLE_SELECT

    def is_valid(self):
        country = shipping.utils.get_selected_shipping_country(self.request)
        cache_key = u'country_values_{}'.format(self.pk)
        countries = cache.get(cache_key)
        if countries is None:
            countries = list(self.value.values_list('id', flat=True))
            cache.set(cache_key, countries)

        if self.operator == self.IS_SELECTED:
            return country.pk in countries
        return country.pk not in countries

    class Meta:
        app_label = 'criteria'


class HeightCriterion(Criterion):
    """
    Criterion to check against product's height / cart's total height.
    """
    value = models.FloatField(_(u"Height"), default=0.0)

    def get_operators(self):
        """
        Returns the available operators for the criterion.
        """
        return self.NUMBER_OPERATORS

    def is_valid(self):
        """
        If product is given, the height is taken from the product, otherwise it
        is the total height of all products within the cart.
        """
        if self.product:
            height = self.product.get_height()
        elif self.cart:
            height = sum([item.product.get_height() * item.amount for item in self.cart.get_items()])
        else:
            height = 0

        if (self.operator == self.EQUAL) and (height == self.value):
            return True
        elif (self.operator == self.LESS_THAN) and (height < self.value):
            return True
        elif (self.operator == self.LESS_THAN_EQUAL) and (height <= self.value):
            return True
        elif (self.operator == self.GREATER_THAN) and (height > self.value):
            return True
        elif (self.operator == self.GREATER_THAN_EQUAL) and (height >= self.value):
            return True
        else:
            return False

    class Meta:
        app_label = 'criteria'


class LengthCriterion(Criterion):
    """
    Criterion to check against product's length / cart's max length.
    """
    value = models.FloatField(_(u"Length"), default=0.0)

    def get_operators(self):
        """
        Returns the available operators for the criterion.
        """
        return self.NUMBER_OPERATORS

    def is_valid(self):
        """
        If product is given, the length is taken from the product otherwise it
        is the max length of all products within the cart.
        """
        if self.product:
            max_length = self.product.get_length()
        elif self.cart and self.cart.get_items():
            max_length = max([item.product.get_length() for item in self.cart.get_items()])
        else:
            max_length = 0

        if (self.operator == self.LESS_THAN) and (max_length < self.value):
            return True
        elif (self.operator == self.LESS_THAN_EQUAL) and (max_length <= self.value):
            return True
        elif (self.operator == self.GREATER_THAN) and (max_length > self.value):
            return True
        elif (self.operator == self.GREATER_THAN_EQUAL) and (max_length >= self.value):
            return True
        elif (self.operator == self.EQUAL) and (max_length == self.value):
            return True
        else:
            return False

    class Meta:
        app_label = 'criteria'


class PaymentMethodCriterion(Criterion):
    """
    Criterion to check against payment methods.
    """
    value = models.ManyToManyField(PaymentMethod, verbose_name=_(u"Payment methods"))

    def get_operators(self):
        """
        Returns the available operators for the criterion.
        """
        return self.SELECTION_OPERATORS + self.VALID_OPERATORS

    def get_selectable_values(self, request):
        selected_payment_methods = self.value.all()
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

        return payment_methods

    def get_value_type(self):
        return self.MULTIPLE_SELECT

    def is_valid(self):
        # see ShippingMethodCriterion for what's going on here
        import lfs.payment.utils
        if isinstance(self.content, PaymentMethod):
            is_payment_method = True
        else:
            is_payment_method = False

        if (not is_payment_method) and (self.operator == self.IS_SELECTED):
            payment_method = lfs.payment.utils.get_selected_payment_method(self.request)
            return payment_method in self.value.all()
        elif (not is_payment_method) and (self.operator == self.IS_NOT_SELECTED):
            payment_method = lfs.payment.utils.get_selected_payment_method(self.request)
            return payment_method not in self.value.all()
        elif self.operator == self.IS_VALID:
            for pm in self.value.all():
                if not pm.is_valid(self.request, self.product):
                    return False
            return True
        elif self.operator == self.IS_NOT_VALID:
            for pm in self.value.all():
                if pm.is_valid(self.request, self.product):
                    return False
            return True
        else:
            return False

    class Meta:
        app_label = 'criteria'


class ShippingMethodCriterion(Criterion):
    """
    Criterion to check against shipping methods.
    """
    value = models.ManyToManyField(ShippingMethod, verbose_name=_(u"Shipping methods"))

    def get_operators(self):
        """
        Returns the available operators for the criterion.
        """
        return self.SELECTION_OPERATORS + self.VALID_OPERATORS

    def get_selectable_values(self, request):
        selected_shipping_methods = self.value.all()
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

        return shipping_methods

    def get_value_type(self):
        return self.MULTIPLE_SELECT

    def is_valid(self):
        # Check whether the criteria is used of a shipping method. If so the
        # operator IS_SELECTED and IS_NOT_SELECTED are not allowed. The reason
        # why we have to check this is that the get_selected_shipping_method
        # checks for valid shipping methods and call this method again, so that
        # we get an infinte recursion.

        import lfs.shipping.utils
        if isinstance(self.content, ShippingMethod):
            is_shipping_method = True
        else:
            is_shipping_method = False

        if (not is_shipping_method) and (self.operator == self.IS_SELECTED):
            shipping_method = lfs.shipping.utils.get_selected_shipping_method(self.request)
            return shipping_method in self.value.all()
        elif (not is_shipping_method) and (self.operator == self.IS_NOT_SELECTED):
            shipping_method = lfs.shipping.utils.get_selected_shipping_method(self.request)
            return shipping_method not in self.value.all()
        elif self.operator == self.IS_VALID:
            for sm in self.value.all():
                if not sm.is_valid(self.request, self.product):
                    return False
            return True
        elif self.operator == self.IS_NOT_VALID:
            for sm in self.value.all():
                if sm.is_valid(self.request, self.product):
                    return False
            return True
        else:
            return False

    class Meta:
        app_label = 'criteria'


class WeightCriterion(Criterion):
    """
    Criterion to check against product's weight / cart's total weight.
    """
    value = models.FloatField(_(u"Weight"), default=0.0)

    def get_operators(self):
        """
        Returns the available operators for the criterion.
        """
        return self.NUMBER_OPERATORS

    def is_valid(self):
        """
        If product is given, the weigth is taken from the product, otherwise it
        is the total weight of all products within the cart.
        """
        if self.product:
            weight = self.product.get_weight()
        elif self.cart:
            weight = sum([item.product.get_weight() * item.amount for item in self.cart.get_items()])
        else:
            weight = 0

        if (self.operator == self.LESS_THAN) and (weight < self.value):
            return True
        elif (self.operator == self.LESS_THAN_EQUAL) and (weight <= self.value):
            return True
        elif (self.operator == self.GREATER_THAN) and (weight > self.value):
            return True
        elif (self.operator == self.GREATER_THAN_EQUAL) and (weight >= self.value):
            return True
        elif (self.operator == self.EQUAL) and (weight == self.value):
            return True
        else:
            return False

    class Meta:
        app_label = 'criteria'


class WidthCriterion(Criterion):
    """
    Criterion to check against product's width / cart's max width.
    """
    value = models.FloatField(_(u"Width"), default=0.0)

    def get_operators(self):
        """
        Returns the available operators for the criterion.
        """
        return self.NUMBER_OPERATORS

    def is_valid(self):
        """
        If product is given, the width is taken from the product, otherwise it
        is the max width of all products within the cart.
        """
        if self.product:
            max_width = self.product.get_width()
        elif self.cart and self.cart.get_items():
            max_width = max([item.product.get_width() for item in self.cart.get_items()])
        else:
            max_width = 0

        if self.operator == self.LESS_THAN and (max_width < self.value):
            return True
        if self.operator == self.LESS_THAN_EQUAL and (max_width <= self.value):
            return True
        if self.operator == self.GREATER_THAN and (max_width > self.value):
            return True
        if self.operator == self.GREATER_THAN_EQUAL and (max_width >= self.value):
            return True
        if self.operator == self.EQUAL and (max_width == self.value):
            return True

        return False

    class Meta:
        app_label = 'criteria'
