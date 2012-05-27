# django imports
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _


# lfs imports
from lfs.core.models import Country
from lfs.shipping.models import ShippingMethod
from lfs.payment.models import PaymentMethod


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

    sa_content_type = models.ForeignKey(ContentType, related_name="sa_content_type")
    sa_object_id = models.PositiveIntegerField()
    selected_shipping_address = generic.GenericForeignKey('sa_content_type', 'sa_object_id')

    ia_content_type = models.ForeignKey(ContentType, related_name="ia_content_type")
    ia_object_id = models.PositiveIntegerField()
    selected_invoice_address = generic.GenericForeignKey('ia_content_type', 'ia_object_id')

    selected_country = models.ForeignKey(Country, verbose_name=_(u"Selected country"), blank=True, null=True)

    def __unicode__(self):
        return "%s/%s" % (self.user, self.session)

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
        return "%s / %s" % (self.account_number, self.bank_name)


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
        return "%s / %s" % (self.type, self.owner)
