from copy import deepcopy

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lfs.addresses import settings
from lfs.core.models import Country
from lfs.payment.models import PaymentMethod
from lfs.shipping.models import ShippingMethod


class Customer(models.Model):
    """
    A customer holds all shop customer related information and is assigned to
    a Django user and/or a session dependend on the login state of the current
    user.

    A customer is only created when it needs to. Either when:

       * The cart is refreshed (this is because some of the customer related
         information could be changed like shipping/payment method or shipping
         address).

       * The customer browses to the check out page.
    """
    user = models.ForeignKey(User, blank=True, null=True)
    session = models.CharField(blank=True, max_length=100)

    selected_shipping_method = models.ForeignKey(ShippingMethod, verbose_name=_(u"Selected shipping method"), blank=True, null=True, related_name="selected_shipping_method")
    selected_payment_method = models.ForeignKey(PaymentMethod, verbose_name=_(u"Selected payment method"), blank=True, null=True, related_name="selected_payment_method")
    selected_bank_account = models.ForeignKey("BankAccount", verbose_name=_(u"Bank account"), blank=True, null=True, related_name="selected_bank_account")
    selected_credit_card = models.ForeignKey("CreditCard", verbose_name=_(u"Credit card"), blank=True, null=True, related_name="selected_credit_card")

    sa_content_type = models.ForeignKey(ContentType, related_name="sa_content_type", null=True)
    sa_object_id = models.PositiveIntegerField(null=True)
    selected_shipping_address = GenericForeignKey('sa_content_type', 'sa_object_id')

    dsa_object_id = models.PositiveIntegerField(null=True)
    default_shipping_address = GenericForeignKey('sa_content_type', 'dsa_object_id')

    ia_content_type = models.ForeignKey(ContentType, related_name="ia_content_type", null=True)
    ia_object_id = models.PositiveIntegerField(null=True)
    selected_invoice_address = GenericForeignKey('ia_content_type', 'ia_object_id')

    dia_object_id = models.PositiveIntegerField(null=True)
    default_invoice_address = GenericForeignKey('ia_content_type', 'dia_object_id')

    selected_country = models.ForeignKey(Country, verbose_name=_(u"Selected country"), blank=True, null=True)

    def __unicode__(self):
        return u"%s/%s" % (self.user, self.session)

    def get_email_address(self):
        """Returns the email address of the customer dependend on the user is
        registered or not.
        """
        if self.user:
            return self.user.email
        elif self.selected_invoice_address:
            return self.selected_invoice_address.email
        else:
            return None

    def set_email_address(self, email):
        """Returns the email address of the customer dependend on the user is
        registered or not.
        """
        if self.user:
            self.user.email = email
            self.user.save()
        else:
            self.selected_invoice_address.email = email
            self.selected_invoice_address.save()

    def get_selected_shipping_address(self):
        """Returns the selected shipping address.
        """
        return self.selected_shipping_address or \
            self.selected_invoice_address or \
            None

    def sync_default_to_selected_addresses(self, force=False):
        # Synchronize selected addresses with default addresses
        auto_update = settings.AUTO_UPDATE_DEFAULT_ADDRESSES
        if force or not auto_update:
            shipping_address = deepcopy(self.default_shipping_address)
            if self.selected_shipping_address:
                shipping_address.id = self.selected_shipping_address.id
                shipping_address.pk = self.selected_shipping_address.pk
                shipping_address.save()
            else:
                shipping_address.id = None
                shipping_address.pk = None
                shipping_address.save()
                self.save()  # save customer to set generic key id

            invoice_address = deepcopy(self.default_invoice_address)
            if self.selected_invoice_address:
                invoice_address.id = self.selected_invoice_address.id
                invoice_address.pk = self.selected_invoice_address.pk
                invoice_address.save()
            else:
                invoice_address.id = None
                invoice_address.pk = None
                invoice_address.save()
                self.save()

    def sync_selected_to_default_invoice_address(self, force=False):
        # Synchronize default invoice address with selected address
        auto_update = settings.AUTO_UPDATE_DEFAULT_ADDRESSES
        if force or auto_update:
            address = deepcopy(self.selected_invoice_address)
            address.id = self.default_invoice_address.id
            address.pk = self.default_invoice_address.pk
            address.save()

    def sync_selected_to_default_shipping_address(self, force=False):
        # Synchronize default shipping address with selected address
        auto_update = settings.AUTO_UPDATE_DEFAULT_ADDRESSES
        if force or auto_update:
            address = deepcopy(self.selected_shipping_address)
            address.id = self.default_shipping_address.id
            address.pk = self.default_shipping_address.pk
            address.save()

    def sync_selected_to_default_addresses(self, force=False):
        # Synchronize default addresses with selected addresses
        self.sync_selected_to_default_invoice_address(force)
        self.sync_selected_to_default_shipping_address(force)

    class Meta:
        app_label = 'customer'


class BankAccount(models.Model):
    """
    Stores all shop relevant data of a credit card.

    **Attributes**

    customer
        The customer the bank accoun belongs to.

    account_number
        The account number of the bank account.

    bank_identification_code
        The bank identification code of the bank account.

    depositor
        The depositor of the bank account.
    """
    customer = models.ForeignKey(Customer, verbose_name=_(u"Customer"), blank=True, null=True, related_name="bank_accounts")
    account_number = models.CharField(_(u"Account number"), blank=True, max_length=30)
    bank_identification_code = models.CharField(_(u"Bank identification code"), blank=True, max_length=30)
    bank_name = models.CharField(_(u"Bank name"), blank=True, max_length=100)
    depositor = models.CharField(_(u"Depositor"), blank=True, max_length=100)

    def __unicode__(self):
        return u"%s / %s" % (self.account_number, self.bank_name)

    class Meta:
        app_label = 'customer'


class CreditCard(models.Model):
    """
    Stores all shop relevant data of a credit card.

    **Attributes:**

    type
        The type of the credit card, like Master Card, Visa, etc.

    owner
        The owner of the credit card.

    number
        The number of the credit card.

    expiration_date_month
        The month of the expiration date of the credit card.

    expiration_date_year
        The year of the expiration date of the credit card.
    """
    customer = models.ForeignKey(Customer, verbose_name=_(u"Customer"), blank=True, null=True, related_name="credit_cards")

    type = models.CharField(_(u"Type"), blank=True, max_length=30)
    owner = models.CharField(_(u"Owner"), blank=True, max_length=100)
    number = models.CharField(_(u"Number"), blank=True, max_length=30)
    expiration_date_month = models.IntegerField(_(u"Expiration date month"), blank=True, null=True)
    expiration_date_year = models.IntegerField(_(u"Expiration date year"), blank=True, null=True)

    def __unicode__(self):
        return u"%s / %s" % (self.type, self.owner)

    class Meta:
        app_label = 'customer'
