# django imports
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.payment.utils
from lfs.catalog.models import Product
from lfs.catalog.models import Property
from lfs.catalog.models import PropertyOption
from lfs.core.models import Country
from lfs.order.settings import ORDER_STATES
from lfs.order.settings import SUBMITTED
from lfs.shipping.models import ShippingMethod
from lfs.payment.models import PaymentMethod
from lfs.payment.settings import PAYPAL

# other imports
import uuid


def get_unique_id_str():
    return str(uuid.uuid4())


class Order(models.Model):
    """An order is created when products have been sold.

    **Parameters**:

    voucher_number, voucher_value, voucher_tax

        Storing this information here assures that we have it all time, even
        when the involved voucher will be deleted.

    requested_delivery_date
        a buyer requested delivery date (e.g. for a florist to deliver flowers on a specific date)

    pay_link
        A link to re-pay the order (e.g. for PayPal)

    """
    user = models.ForeignKey(User, verbose_name=_(u"User"), blank=True, null=True)
    session = models.CharField(_(u"Session"), blank=True, max_length=100)

    created = models.DateTimeField(_(u"Created"), auto_now_add=True)

    state = models.PositiveSmallIntegerField(_(u"State"), choices=ORDER_STATES, default=SUBMITTED)
    state_modified = models.DateTimeField(_(u"State modified"), auto_now_add=True)

    price = models.FloatField(_(u"Price"), default=0.0)
    tax = models.FloatField(_(u"Tax"), default=0.0)

    customer_firstname = models.CharField(_(u"firstname"), max_length=50)
    customer_lastname = models.CharField(_(u"lastname"), max_length=50)
    customer_email = models.CharField(_(u"email"), max_length=50)

    invoice_firstname = models.CharField(_(u"Invoice firstname"), max_length=50)
    invoice_lastname = models.CharField(_(u"Invoice lastname"), max_length=50)
    invoice_line1 = models.CharField(_(u"Invoice Line 1"), null=True, blank=True, max_length=100)
    invoice_line2 = models.CharField(_(u"Invoice Line 2"), null=True, blank=True, max_length=100)
    invoice_city = models.CharField(_(u"Invoice City"), null=True, blank=True, max_length=100)
    invoice_state = models.CharField(_(u"Invoice State"), null=True, blank=True, max_length=100)
    invoice_code = models.CharField(_(u"Invoice Postal Code"), null=True, blank=True, max_length=100)
    invoice_country = models.ForeignKey(Country, related_name="orders_invoice_country", blank=True, null=True)
    invoice_phone = models.CharField(_(u"Invoice phone"), blank=True, max_length=20)

    shipping_firstname = models.CharField(_(u"Shipping firstname"), max_length=50)
    shipping_lastname = models.CharField(_(u"Shipping lastname"), max_length=50)
    shipping_line1 = models.CharField(_(u"Shipping Line 1"), null=True, blank=True, max_length=100)
    shipping_line2 = models.CharField(_(u"Shipping Line 2"), null=True, blank=True, max_length=100)
    shipping_city = models.CharField(_(u"Shipping City"), null=True, blank=True, max_length=100)
    shipping_state = models.CharField(_(u"Shipping State"), null=True, blank=True, max_length=100)
    shipping_code = models.CharField(_(u"Shipping Postal Code"), null=True, blank=True, max_length=100)
    shipping_country = models.ForeignKey(Country, related_name="orders_shipping_country", blank=True, null=True)
    shipping_phone = models.CharField(_(u"Shipping phone"), blank=True, max_length=20)

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

    def __unicode__(self):
        return "%s (%s %s)" % (self.created.strftime("%x %X"), self.customer_firstname, self.customer_lastname)

    def get_pay_link(self):
        """Returns a pay link for the selected payment method.
        """
        return lfs.payment.utils.get_pay_link(self.payment_method, self)

    def get_name(self):
        order_name = ""
        for order_item in self.items.all():
            if order_item.product is not None:
                order_name = order_name + order_item.product.get_name() + ", "

        order_name.strip(', ')
        return order_name


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
    product = models.ForeignKey(Product, blank=True, null=True)

    # Values of the product at the time the orders has been created
    product_amount = models.FloatField(_(u"Product quantity"), blank=True, null=True)
    product_sku = models.CharField(_(u"Product SKU"), blank=True, max_length=100)
    product_name = models.CharField(_(u"Product name"), blank=True, max_length=100)
    product_price_net = models.FloatField(_(u"Product price net"), default=0.0)
    product_price_gross = models.FloatField(_(u"Product price gross"), default=0.0)
    product_tax = models.FloatField(_(u"Product tax"), default=0.0)

    def __unicode__(self):
        return "%s" % self.product_name

    @property
    def amount(self):
        return self.product_amount

    def get_properties(self):
        """Returns properties of the order item. Resolves option names for
        select fields.
        """
        properties = []
        for property_value in self.properties.all():

            if property_value.property.is_select_field:
                try:
                    option = PropertyOption.objects.get(pk=int(float(property_value.value)))
                except (PropertyOption.DoesNotExist, ValueError):
                    value = property_value.value
                    price = 0.0
                else:
                    value = option.name
                    price = option.price
            else:
                format_string = "%%.%sf" % property_value.property.decimal_places
                try:
                    value = format_string % float(property_value.value)
                except ValueError:
                    value = "%.2f" % float(property_value.value)

                price = ""

            properties.append({
                "name": property_value.property.name,
                "title": property_value.property.title,
                "unit": property_value.property.unit,
                "display_price": property_value.property.display_price,
                "value": value,
                "price": price
            })

        return properties


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
