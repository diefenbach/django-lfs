# django imports
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.core.models import Country
from lfs.shipping.models import ShippingMethod
from lfs.payment.models import PaymentMethod


class Customer(models.Model):
    """
    * A customer holds all shop customer related information and is assigned to
      a Django user and/or a session dependend on the login state of the current
      user.
    * A customer is only created when it needs to. Either when:
       - the cart is refreshed (this is because some of the customer related
         information could be changed like shipping/payment method or shipping
         address)
       - the customer browses to the check out page
    """
    user = models.ForeignKey(User, blank=True, null=True)
    session = models.CharField(blank=True, max_length=100)

    selected_shipping_method = models.ForeignKey(ShippingMethod, verbose_name=_(u"Selected shipping method"), blank=True, null=True, related_name="selected_shipping_method")
    selected_payment_method = models.ForeignKey(PaymentMethod, verbose_name=_(u"Selected payment method"), blank=True, null=True, related_name="selected_payment_method")
    selected_bank_account = models.ForeignKey("BankAccount", verbose_name=_(u"Bank account"), blank=True, null=True, related_name="selected_bank_account")
    selected_credit_card = models.ForeignKey("CreditCard", verbose_name=_(u"Credit card"), blank=True, null=True, related_name="selected_credit_card")
    selected_shipping_address = models.ForeignKey("Address", verbose_name=_(u"Selected shipping address"), blank=True, null=True, related_name="selected_shipping_address")
    selected_invoice_address = models.ForeignKey("Address", verbose_name=_(u"Selected invoice address"), blank=True, null=True, related_name="selected_invoice_address")
    selected_country = models.ForeignKey(Country, verbose_name=_(u"Selected country"), blank=True, null=True)

    def __unicode__(self):
        return "%s/%s" % (self.user, self.session)

    def get_email_address(self):
        """Returns the email address of the customer dependend on the user is
        registered or not.
        """
        if self.user:
            return self.user.email
        else:
            return self.selected_invoice_address.email

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


class Address(models.Model):
    """An address which can be used as shipping and/or invoice address.
    """
    customer = models.ForeignKey(Customer, verbose_name=_(u"Customer"), blank=True, null=True, related_name="addresses")

    firstname = models.CharField(_("Firstname"), max_length=50)
    lastname = models.CharField(_("Lastname"), max_length=50)
    company_name = models.CharField(_("Company name"), max_length=50, blank=True, null=True)
    street = models.CharField(_("Street"), max_length=100)
    zip_code = models.CharField(_("Zip code"), max_length=10)
    city = models.CharField(_("City"), max_length=50)
    state = models.CharField(_("State"), max_length=50, blank=True)
    country = models.ForeignKey(Country, verbose_name=_("Country"), blank=True, null=True)
    phone = models.CharField(_("Phone"), blank=True, max_length=20)
    email = models.EmailField(_("E-Mail"), blank=True, null=True, max_length=50)

    def __unicode__(self):
        return "%s / %s" % (self.street, self.city)


class BankAccount(models.Model):
    """Stores all shop relevant data of a bank account an belongs to a customer.
    """
    customer = models.ForeignKey(Customer, verbose_name=_(u"Customer"), blank=True, null=True, related_name="bank_accounts")

    account_number = models.CharField(_(u"Account number"), blank=True, max_length=30)
    bank_identification_code = models.CharField(_(u"Bank identification code"), blank=True, max_length=30)
    bank_name = models.CharField(_(u"Bank name"), blank=True, max_length=100)
    depositor = models.CharField(_(u"Depositor"), blank=True, max_length=100)

    def __unicode__(self):
        return "%s / %s" % (self.account_number, self.bank_name)


class CreditCard(models.Model):
    """Stores all shop relevant data of a credit cart and belongs to a customer.
    """
    customer = models.ForeignKey(Customer, verbose_name=_(u"Customer"), blank=True, null=True, related_name="credit_cards")

    type = models.CharField(_(u"Type"), blank=True, max_length=30)
    owner = models.CharField(_(u"Owner"), blank=True, max_length=100)
    number = models.CharField(_(u"Number"), blank=True, max_length=30)
    expiration_date_month = models.IntegerField(_(u"Expiration date month"), )
    expiration_date_year = models.IntegerField(_(u"Expiration date year"), )

    def __unicode__(self):
        return "%s / %s" % (self.card_type, self.card_owner)
