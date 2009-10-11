
from south.db import db
from django.db import models
from lfs.customer.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'CreditCard'
        db.create_table('customer_creditcard', (
            ('customer', models.ForeignKey(orm.Customer, related_name="credit_cards", null=True, verbose_name=_(u"Customer"), blank=True)),
            ('number', models.CharField(_(u"Number"), max_length=30, blank=True)),
            ('expiration_date_year', models.IntegerField(_(u"Expiration date year"))),
            ('expiration_date_month', models.IntegerField(_(u"Expiration date month"))),
            ('owner', models.CharField(_(u"Owner"), max_length=100, blank=True)),
            ('type', models.CharField(_(u"Type"), max_length=30, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('customer', ['CreditCard'])
        
        # Adding model 'BankAccount'
        db.create_table('customer_bankaccount', (
            ('customer', models.ForeignKey(orm.Customer, related_name="bank_accounts", null=True, verbose_name=_(u"Customer"), blank=True)),
            ('bank_name', models.CharField(_(u"Bank name"), max_length=100, blank=True)),
            ('bank_identification_code', models.CharField(_(u"Bank identification code"), max_length=30, blank=True)),
            ('depositor', models.CharField(_(u"Depositor"), max_length=100, blank=True)),
            ('account_number', models.CharField(_(u"Account number"), max_length=30, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('customer', ['BankAccount'])
        
        # Adding model 'Address'
        db.create_table('customer_address', (
            ('customer', models.ForeignKey(orm.Customer, related_name="addresses", null=True, verbose_name=_(u"Customer"), blank=True)),
            ('city', models.CharField(_("City"), max_length=50)),
            ('firstname', models.CharField(_("Firstname"), max_length=50)),
            ('lastname', models.CharField(_("Lastname"), max_length=50)),
            ('email', models.EmailField(_("E-Mail"), max_length=50, null=True, blank=True)),
            ('phone', models.CharField(_("Phone"), max_length=20, blank=True)),
            ('street', models.CharField(_("Street"), max_length=100)),
            ('country', models.ForeignKey(orm['core.Country'], verbose_name=_("Country"))),
            ('id', models.AutoField(primary_key=True)),
            ('zip_code', models.CharField(_("Zip code"), max_length=10)),
        ))
        db.send_create_signal('customer', ['Address'])
        
        # Adding model 'Customer'
        db.create_table('customer_customer', (
            ('selected_shipping_method', models.ForeignKey(orm['shipping.ShippingMethod'], related_name="selected_shipping_method", null=True, verbose_name=_(u"Selected shipping method"), blank=True)),
            ('selected_bank_account', models.ForeignKey(orm.BankAccount, related_name="selected_bank_account", null=True, verbose_name=_(u"Bank account"), blank=True)),
            ('selected_invoice_address', models.ForeignKey(orm.Address, related_name="selected_invoice_address", null=True, verbose_name=_(u"Selected invoice address"), blank=True)),
            ('selected_shipping_address', models.ForeignKey(orm.Address, related_name="selected_shipping_address", null=True, verbose_name=_(u"Selected shipping address"), blank=True)),
            ('session', models.CharField(max_length=100, blank=True)),
            ('user', models.ForeignKey(orm['auth.User'], null=True, blank=True)),
            ('selected_payment_method', models.ForeignKey(orm['payment.PaymentMethod'], related_name="selected_payment_method", null=True, verbose_name=_(u"Selected payment method"), blank=True)),
            ('selected_country', models.ForeignKey(orm['core.Country'], null=True, verbose_name=_(u"Selected country"), blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('selected_credit_card', models.ForeignKey(orm.CreditCard, related_name="selected_credit_card", null=True, verbose_name=_(u"Credit card"), blank=True)),
        ))
        db.send_create_signal('customer', ['Customer'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'CreditCard'
        db.delete_table('customer_creditcard')
        
        # Deleting model 'BankAccount'
        db.delete_table('customer_bankaccount')
        
        # Deleting model 'Address'
        db.delete_table('customer_address')
        
        # Deleting model 'Customer'
        db.delete_table('customer_customer')
        
    
    
    models = {
        'customer.creditcard': {
            'customer': ('models.ForeignKey', ['Customer'], {'related_name': '"credit_cards"', 'null': 'True', 'verbose_name': '_(u"Customer")', 'blank': 'True'}),
            'expiration_date_month': ('models.IntegerField', ['_(u"Expiration date month")'], {}),
            'expiration_date_year': ('models.IntegerField', ['_(u"Expiration date year")'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'number': ('models.CharField', ['_(u"Number")'], {'max_length': '30', 'blank': 'True'}),
            'owner': ('models.CharField', ['_(u"Owner")'], {'max_length': '100', 'blank': 'True'}),
            'type': ('models.CharField', ['_(u"Type")'], {'max_length': '30', 'blank': 'True'})
        },
        'payment.paymentmethod': {
            'Meta': {'ordering': '("priority",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'customer.customer': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'selected_bank_account': ('models.ForeignKey', ['"BankAccount"'], {'related_name': '"selected_bank_account"', 'null': 'True', 'verbose_name': '_(u"Bank account")', 'blank': 'True'}),
            'selected_country': ('models.ForeignKey', ['Country'], {'null': 'True', 'verbose_name': '_(u"Selected country")', 'blank': 'True'}),
            'selected_credit_card': ('models.ForeignKey', ['"CreditCard"'], {'related_name': '"selected_credit_card"', 'null': 'True', 'verbose_name': '_(u"Credit card")', 'blank': 'True'}),
            'selected_invoice_address': ('models.ForeignKey', ['"Address"'], {'related_name': '"selected_invoice_address"', 'null': 'True', 'verbose_name': '_(u"Selected invoice address")', 'blank': 'True'}),
            'selected_payment_method': ('models.ForeignKey', ['PaymentMethod'], {'related_name': '"selected_payment_method"', 'null': 'True', 'verbose_name': '_(u"Selected payment method")', 'blank': 'True'}),
            'selected_shipping_address': ('models.ForeignKey', ['"Address"'], {'related_name': '"selected_shipping_address"', 'null': 'True', 'verbose_name': '_(u"Selected shipping address")', 'blank': 'True'}),
            'selected_shipping_method': ('models.ForeignKey', ['ShippingMethod'], {'related_name': '"selected_shipping_method"', 'null': 'True', 'verbose_name': '_(u"Selected shipping method")', 'blank': 'True'}),
            'session': ('models.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'null': 'True', 'blank': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'customer.address': {
            'city': ('models.CharField', ['_("City")'], {'max_length': '50'}),
            'country': ('models.ForeignKey', ['Country'], {'verbose_name': '_("Country")'}),
            'customer': ('models.ForeignKey', ['Customer'], {'related_name': '"addresses"', 'null': 'True', 'verbose_name': '_(u"Customer")', 'blank': 'True'}),
            'email': ('models.EmailField', ['_("E-Mail")'], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'firstname': ('models.CharField', ['_("Firstname")'], {'max_length': '50'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('models.CharField', ['_("Lastname")'], {'max_length': '50'}),
            'phone': ('models.CharField', ['_("Phone")'], {'max_length': '20', 'blank': 'True'}),
            'street': ('models.CharField', ['_("Street")'], {'max_length': '100'}),
            'zip_code': ('models.CharField', ['_("Zip code")'], {'max_length': '10'})
        },
        'shipping.shippingmethod': {
            'Meta': {'ordering': '("priority",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'customer.bankaccount': {
            'account_number': ('models.CharField', ['_(u"Account number")'], {'max_length': '30', 'blank': 'True'}),
            'bank_identification_code': ('models.CharField', ['_(u"Bank identification code")'], {'max_length': '30', 'blank': 'True'}),
            'bank_name': ('models.CharField', ['_(u"Bank name")'], {'max_length': '100', 'blank': 'True'}),
            'customer': ('models.ForeignKey', ['Customer'], {'related_name': '"bank_accounts"', 'null': 'True', 'verbose_name': '_(u"Customer")', 'blank': 'True'}),
            'depositor': ('models.CharField', ['_(u"Depositor")'], {'max_length': '100', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.country': {
            'Meta': {'ordering': '("name",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['customer']
