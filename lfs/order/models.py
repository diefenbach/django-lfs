# python imports
import uuid

# django imports
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.payment.utils
import lfs.core.utils
import lfs.catalog.models
from lfs.catalog.models import Product
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption
from lfs.catalog.models import DeliveryTimeBase
from lfs.order.settings import ORDER_STATES, SUBMITTED, PAYMENT_FAILED, PAYMENT_FLAGGED
from lfs.shipping.models import ShippingMethod
from lfs.payment.models import PaymentMethod


def get_unique_id_str():
    return str(uuid.uuid4())


class Order(models.Model):
    """
    An order is created when products have been sold.

    **Attributes:**

    number
        The unique order number of the order, which is the reference for the
        customer.

    voucher_number, voucher_value, voucher_tax
        Storing this information here assures that we have it all time, even
        when the involved voucher will be deleted.

    requested_delivery_date
        A buyer requested delivery date (e.g. for a florist to deliver flowers
        on a specific date)

    pay_link
        A link to re-pay the order (e.g. for PayPal)

    invoice_address_id
        The invoice address of the order (this is not a FK because of circular
        imports).

    shipping_address_id
        The shipping address of the order (this is not a FK because of circular
        imports).

    """
    number = models.CharField(max_length=30)
    user = models.ForeignKey(User, verbose_name=_(u"User"), blank=True, null=True)
    session = models.CharField(_(u"Session"), blank=True, max_length=100)

    created = models.DateTimeField(_(u"Created"), auto_now_add=True)

    state = models.PositiveSmallIntegerField(_(u"State"), choices=ORDER_STATES, default=SUBMITTED)
    state_modified = models.DateTimeField(_(u"State modified"), auto_now_add=True)

    price = models.FloatField(_(u"Price"), default=0.0)
    tax = models.FloatField(_(u"Tax"), default=0.0)

    customer_firstname = models.CharField(_(u"firstname"), max_length=50)
    customer_lastname = models.CharField(_(u"lastname"), max_length=50)
    customer_email = models.CharField(_(u"email"), max_length=75)

    sa_content_type = models.ForeignKey(ContentType, related_name="order_shipping_address")
    sa_object_id = models.PositiveIntegerField()
    shipping_address = GenericForeignKey('sa_content_type', 'sa_object_id')

    ia_content_type = models.ForeignKey(ContentType, related_name="order_invoice_address")
    ia_object_id = models.PositiveIntegerField()
    invoice_address = GenericForeignKey('ia_content_type', 'ia_object_id')

    shipping_method = models.ForeignKey(ShippingMethod, verbose_name=_(u"Shipping Method"), blank=True, null=True)
    shipping_price = models.FloatField(_(u"Shipping Price"), default=0.0)
    shipping_tax = models.FloatField(_(u"Shipping Tax"), default=0.0)

    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_(u"Payment Method"), blank=True, null=True)
    payment_price = models.FloatField(_(u"Payment Price"), default=0.0)
    payment_tax = models.FloatField(_(u"Payment Tax"), default=0.0)

    account_number = models.CharField(_(u"Account number"), blank=True, max_length=30)
    bank_identification_code = models.CharField(_(u"Bank identication code"), blank=True, max_length=30)
    bank_name = models.CharField(_(u"Bank name"), blank=True, max_length=100)
    depositor = models.CharField(_(u"Depositor"), blank=True, max_length=100)

    voucher_number = models.CharField(_(u"Voucher number"), blank=True, max_length=100)
    voucher_price = models.FloatField(_(u"Voucher value"), default=0.0)
    voucher_tax = models.FloatField(_(u"Voucher tax"), default=0.0)

    message = models.TextField(_(u"Message"), blank=True)
    pay_link = models.TextField(_(u"pay_link"), blank=True)

    uuid = models.CharField(max_length=50, editable=False, unique=True, default=get_unique_id_str)
    requested_delivery_date = models.DateTimeField(_(u"Delivery Date"), null=True, blank=True)

    class Meta:
        ordering = ("-created", )
        app_label = 'order'

    def __unicode__(self):
        return u"%s (%s %s)" % (self.created.strftime("%x %X"), self.customer_firstname, self.customer_lastname)

    def get_pay_link(self, request=None):
        """
        Returns a pay link for the selected payment method.
        """
        if self.payment_method.module:
            payment_class = lfs.core.utils.import_symbol(self.payment_method.module)
            payment_instance = payment_class(request=request, order=self)
            try:
                return payment_instance.get_pay_link()
            except AttributeError:
                return ""
        else:
            return ""

    def can_be_paid(self):
        return self.state in (SUBMITTED, PAYMENT_FAILED, PAYMENT_FLAGGED)

    def get_name(self):
        order_name = ""
        for order_item in self.items.all():
            if order_item.product is not None:
                order_name = order_name + order_item.product.get_name() + ", "

        return order_name.strip(', ')

    def price_net(self):
        return self.price - self.tax

    def get_delivery_time(self):
        try:
            return self.delivery_time
        except OrderDeliveryTime.DoesNotExist:
            return None


class OrderItem(models.Model):
    """An order items holds the sold product, its amount and some other relevant
    product values like the price at the time the product has been sold.
    """
    order = models.ForeignKey(Order, related_name="items")

    price_net = models.FloatField(_(u"Price net"), default=0.0)
    price_gross = models.FloatField(_(u"Price gross"), default=0.0)
    tax = models.FloatField(_(u"Tax"), default=0.0)

    # A optional reference to the origin product. This is optional in case the
    # product has been deleted. TODO: Decide: Are products able to be delete?
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)

    # Values of the product at the time the orders has been created
    product_amount = models.FloatField(_(u"Product quantity"), blank=True, null=True)
    product_sku = models.CharField(_(u"Product SKU"), blank=True, max_length=100)
    product_name = models.CharField(_(u"Product name"), blank=True, max_length=100)
    product_price_net = models.FloatField(_(u"Product price net"), default=0.0)
    product_price_gross = models.FloatField(_(u"Product price gross"), default=0.0)
    product_tax = models.FloatField(_(u"Product tax"), default=0.0)

    def __unicode__(self):
        return u"%s" % self.product_name

    @property
    def amount(self):
        if self.product:
            return self.product.get_clean_quantity(self.product_amount)
        else:
            try:
                return int(self.product_amount)
            except (ValueError, TypeError):
                return 1

    def get_properties(self):
        """Returns properties of the order item. Resolves option names for
        select fields.
        """
        properties = []
        for property_value in self.properties.all():
            price = ""
            if property_value.property.is_select_field:
                try:
                    option = PropertyOption.objects.get(pk=int(float(property_value.value)))
                except (PropertyOption.DoesNotExist, ValueError):
                    value = property_value.value
                    price = 0.0
                else:
                    value = option.name
                    price = option.price
            elif property_value.property.is_number_field:
                format_string = "%%.%sf" % property_value.property.decimal_places
                try:
                    value = format_string % float(property_value.value)
                except ValueError:
                    value = "%.2f" % float(property_value.value)
            else:
                value = property_value.value

            properties.append({
                "name": property_value.property.name,
                "title": property_value.property.title,
                "unit": property_value.property.unit,
                "display_price": property_value.property.display_price,
                "value": value,
                "price": price,
                "obj": property_value.property
            })

        return properties

    class Meta:
        app_label = 'order'


class OrderItemPropertyValue(models.Model):
    """Stores a value for a property and order item.

    **Attributes**

    order_item
        The order item - and in this way the product - for which the value
        should be stored.

    property
        The property for which the value should be stored.

    value
        The value which is stored.
    """
    order_item = models.ForeignKey(OrderItem, verbose_name=_(u"Order item"), related_name="properties")
    property = models.ForeignKey(Property, verbose_name=_(u"Property"))
    value = models.CharField("Value", blank=True, max_length=100)

    class Meta:
        app_label = 'order'


class OrderDeliveryTime(DeliveryTimeBase):
    order = models.OneToOneField(Order, verbose_name=_('Order'), related_name='delivery_time')

    def _get_instance(self, min, max, unit):
        return self.__class__(min=min, max=max, unit=unit, order=self.order)

    def __unicode__(self):
        return u'[{0}] {1}'.format(self.order.number, self.round().as_string())

    class Meta:
        verbose_name = _(u'Order delivery time')
        verbose_name_plural = _(u'Order delivery times')
        app_label = 'order'
