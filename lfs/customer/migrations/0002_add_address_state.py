
from south.db import db
from django.db import models
from lfs.customer.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Address.state'
        db.add_column('customer_address', 'state', models.CharField(_("State"), max_length=50, blank=True))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Address.state'
        db.delete_column('customer_address', 'state')
        
    
    
    models = {
        'customer.creditcard': {
            'customer': ('models.ForeignKey', ["orm['customer.Customer']"], {'related_name': '"credit_cards"', 'null': 'True', 'blank': 'True'}),
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
            'selected_bank_account': ('models.ForeignKey', ["orm['customer.BankAccount']"], {'related_name': '"selected_bank_account"', 'null': 'True', 'blank': 'True'}),
            'selected_country': ('models.ForeignKey', ["orm['core.Country']"], {'null': 'True', 'blank': 'True'}),
            'selected_credit_card': ('models.ForeignKey', ["orm['customer.CreditCard']"], {'related_name': '"selected_credit_card"', 'null': 'True', 'blank': 'True'}),
            'selected_invoice_address': ('models.ForeignKey', ["orm['customer.Address']"], {'related_name': '"selected_invoice_address"', 'null': 'True', 'blank': 'True'}),
            'selected_payment_method': ('models.ForeignKey', ["orm['payment.PaymentMethod']"], {'related_name': '"selected_payment_method"', 'null': 'True', 'blank': 'True'}),
            'selected_shipping_address': ('models.ForeignKey', ["orm['customer.Address']"], {'related_name': '"selected_shipping_address"', 'null': 'True', 'blank': 'True'}),
            'selected_shipping_method': ('models.ForeignKey', ["orm['shipping.ShippingMethod']"], {'related_name': '"selected_shipping_method"', 'null': 'True', 'blank': 'True'}),
            'session': ('models.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'shipping.shippingmethod': {
            'Meta': {'ordering': '("priority",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'customer.address': {
            'city': ('models.CharField', ['_("City")'], {'max_length': '50'}),
            'country': ('models.ForeignKey', ["orm['core.Country']"], {}),
            'customer': ('models.ForeignKey', ["orm['customer.Customer']"], {'related_name': '"addresses"', 'null': 'True', 'blank': 'True'}),
            'email': ('models.EmailField', ['_("E-Mail")'], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'firstname': ('models.CharField', ['_("Firstname")'], {'max_length': '50'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('models.CharField', ['_("Lastname")'], {'max_length': '50'}),
            'phone': ('models.CharField', ['_("Phone")'], {'max_length': '20', 'blank': 'True'}),
            'state': ('models.CharField', ['_("State")'], {'max_length': '50', 'blank': 'True'}),
            'street': ('models.CharField', ['_("Street")'], {'max_length': '100'}),
            'zip_code': ('models.CharField', ['_("Zip code")'], {'max_length': '10'})
        },
        'customer.bankaccount': {
            'account_number': ('models.CharField', ['_(u"Account number")'], {'max_length': '30', 'blank': 'True'}),
            'bank_identification_code': ('models.CharField', ['_(u"Bank identification code")'], {'max_length': '30', 'blank': 'True'}),
            'bank_name': ('models.CharField', ['_(u"Bank name")'], {'max_length': '100', 'blank': 'True'}),
            'customer': ('models.ForeignKey', ["orm['customer.Customer']"], {'related_name': '"bank_accounts"', 'null': 'True', 'blank': 'True'}),
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
