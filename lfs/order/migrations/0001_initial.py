
from south.db import db
from django.db import models
from lfs.order.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'OrderItem'
        db.create_table('order_orderitem', (
            ('product', models.ForeignKey(orm['catalog.Product'], null=True, blank=True)),
            ('product_name', models.CharField(_(u"Product name"), max_length=100, blank=True)),
            ('product_amount', models.IntegerField(_(u"Product quantity"), null=True, blank=True)),
            ('tax', models.FloatField(_(u"Tax"), default=0.0)),
            ('id', models.AutoField(primary_key=True)),
            ('product_price_net', models.FloatField(_(u"Product price net"), default=0.0)),
            ('product_tax', models.FloatField(_(u"Product tax"), default=0.0)),
            ('product_price_gross', models.FloatField(_(u"Product price gross"), default=0.0)),
            ('product_sku', models.CharField(_(u"Product SKU"), max_length=100, blank=True)),
            ('price_net', models.FloatField(_(u"Price net"), default=0.0)),
            ('order', models.ForeignKey(orm.Order, related_name="items")),
            ('price_gross', models.FloatField(_(u"Price gross"), default=0.0)),
        ))
        db.send_create_signal('order', ['OrderItem'])
        
        # Adding model 'Order'
        db.create_table('order_order', (
            ('shipping_method', models.ForeignKey(orm['shipping.ShippingMethod'], null=True, verbose_name=_(u"Shipping Method"), blank=True)),
            ('shipping_street', models.CharField(_(u"Shipping street"), max_length=100, blank=True)),
            ('payment_method', models.ForeignKey(orm['payment.PaymentMethod'], null=True, verbose_name=_(u"Payment Method"), blank=True)),
            ('bank_identification_code', models.CharField(_(u"Bank identication code"), max_length=30, blank=True)),
            ('customer_firstname', models.CharField(_(u"firstname"), max_length=50)),
            ('shipping_zip_code', models.CharField(_(u"Shipping zip code"), max_length=10)),
            ('depositor', models.CharField(_(u"Depositor"), max_length=100, blank=True)),
            ('session', models.CharField(_(u"Session"), max_length=100, blank=True)),
            ('invoice_city', models.CharField(_(u"Invoice city"), max_length=50)),
            ('shipping_firstname', models.CharField(_(u"Shipping firstname"), max_length=50)),
            ('shipping_tax', models.FloatField(_(u"Shipping Tax"), default=0.0)),
            ('id', models.AutoField(primary_key=True)),
            ('shipping_price', models.FloatField(_(u"Shipping Price"), default=0.0)),
            ('invoice_country', models.ForeignKey(orm['core.Country'], related_name="orders_invoice_country")),
            ('shipping_phone', models.CharField(_(u"Shipping phone"), max_length=20, blank=True)),
            ('payment_tax', models.FloatField(_(u"Payment Tax"), default=0.0)),
            ('state', models.PositiveSmallIntegerField(_(u"State"), default=SUBMITTED)),
            ('invoice_zip_code', models.CharField(_(u"Invoice zip code"), max_length=10)),
            ('customer_lastname', models.CharField(_(u"lastname"), max_length=50)),
            ('shipping_lastname', models.CharField(_(u"Shipping lastname"), max_length=50)),
            ('invoice_street', models.CharField(_(u"Invoice street"), max_length=100, blank=True)),
            ('bank_name', models.CharField(_(u"Bank name"), max_length=100, blank=True)),
            ('customer_email', models.CharField(_(u"lastname"), max_length=50)),
            ('shipping_city', models.CharField(_(u"Shipping city"), max_length=50)),
            ('tax', models.FloatField(_(u"Tax"), default=0.0)),
            ('price', models.FloatField(_(u"Price"), default=0.0)),
            ('account_number', models.CharField(_(u"Account number"), max_length=30, blank=True)),
            ('invoice_phone', models.CharField(_(u"Invoice phone"), max_length=20, blank=True)),
            ('user', models.ForeignKey(orm['auth.User'], null=True, verbose_name=_(u"User"), blank=True)),
            ('invoice_firstname', models.CharField(_(u"Invoice firstname"), max_length=50)),
            ('created', models.DateTimeField(_(u"Created"), auto_now_add=True)),
            ('payment_price', models.FloatField(_(u"Payment Price"), default=0.0)),
            ('message', models.TextField(_(u"Message"), blank=True)),
            ('invoice_lastname', models.CharField(_(u"Invoice lastname"), max_length=50)),
            ('shipping_country', models.ForeignKey(orm['core.Country'], related_name="orders_shipping_country")),
        ))
        db.send_create_signal('order', ['Order'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'OrderItem'
        db.delete_table('order_orderitem')
        
        # Deleting model 'Order'
        db.delete_table('order_order')
        
    
    
    models = {
        'order.orderitem': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'order': ('models.ForeignKey', ['Order'], {'related_name': '"items"'}),
            'price_gross': ('models.FloatField', ['_(u"Price gross")'], {'default': '0.0'}),
            'price_net': ('models.FloatField', ['_(u"Price net")'], {'default': '0.0'}),
            'product': ('models.ForeignKey', ['Product'], {'null': 'True', 'blank': 'True'}),
            'product_amount': ('models.IntegerField', ['_(u"Product quantity")'], {'null': 'True', 'blank': 'True'}),
            'product_name': ('models.CharField', ['_(u"Product name")'], {'max_length': '100', 'blank': 'True'}),
            'product_price_gross': ('models.FloatField', ['_(u"Product price gross")'], {'default': '0.0'}),
            'product_price_net': ('models.FloatField', ['_(u"Product price net")'], {'default': '0.0'}),
            'product_sku': ('models.CharField', ['_(u"Product SKU")'], {'max_length': '100', 'blank': 'True'}),
            'product_tax': ('models.FloatField', ['_(u"Product tax")'], {'default': '0.0'}),
            'tax': ('models.FloatField', ['_(u"Tax")'], {'default': '0.0'})
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
        'catalog.product': {
            'Meta': {'ordering': '("name",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'order.order': {
            'Meta': {'ordering': '("-created",)'},
            'account_number': ('models.CharField', ['_(u"Account number")'], {'max_length': '30', 'blank': 'True'}),
            'bank_identification_code': ('models.CharField', ['_(u"Bank identication code")'], {'max_length': '30', 'blank': 'True'}),
            'bank_name': ('models.CharField', ['_(u"Bank name")'], {'max_length': '100', 'blank': 'True'}),
            'created': ('models.DateTimeField', ['_(u"Created")'], {'auto_now_add': 'True'}),
            'customer_email': ('models.CharField', ['_(u"lastname")'], {'max_length': '50'}),
            'customer_firstname': ('models.CharField', ['_(u"firstname")'], {'max_length': '50'}),
            'customer_lastname': ('models.CharField', ['_(u"lastname")'], {'max_length': '50'}),
            'depositor': ('models.CharField', ['_(u"Depositor")'], {'max_length': '100', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'invoice_city': ('models.CharField', ['_(u"Invoice city")'], {'max_length': '50'}),
            'invoice_country': ('models.ForeignKey', ['Country'], {'related_name': '"orders_invoice_country"'}),
            'invoice_firstname': ('models.CharField', ['_(u"Invoice firstname")'], {'max_length': '50'}),
            'invoice_lastname': ('models.CharField', ['_(u"Invoice lastname")'], {'max_length': '50'}),
            'invoice_phone': ('models.CharField', ['_(u"Invoice phone")'], {'max_length': '20', 'blank': 'True'}),
            'invoice_street': ('models.CharField', ['_(u"Invoice street")'], {'max_length': '100', 'blank': 'True'}),
            'invoice_zip_code': ('models.CharField', ['_(u"Invoice zip code")'], {'max_length': '10'}),
            'message': ('models.TextField', ['_(u"Message")'], {'blank': 'True'}),
            'payment_method': ('models.ForeignKey', ['PaymentMethod'], {'null': 'True', 'verbose_name': '_(u"Payment Method")', 'blank': 'True'}),
            'payment_price': ('models.FloatField', ['_(u"Payment Price")'], {'default': '0.0'}),
            'payment_tax': ('models.FloatField', ['_(u"Payment Tax")'], {'default': '0.0'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'}),
            'session': ('models.CharField', ['_(u"Session")'], {'max_length': '100', 'blank': 'True'}),
            'shipping_city': ('models.CharField', ['_(u"Shipping city")'], {'max_length': '50'}),
            'shipping_country': ('models.ForeignKey', ['Country'], {'related_name': '"orders_shipping_country"'}),
            'shipping_firstname': ('models.CharField', ['_(u"Shipping firstname")'], {'max_length': '50'}),
            'shipping_lastname': ('models.CharField', ['_(u"Shipping lastname")'], {'max_length': '50'}),
            'shipping_method': ('models.ForeignKey', ['ShippingMethod'], {'null': 'True', 'verbose_name': '_(u"Shipping Method")', 'blank': 'True'}),
            'shipping_phone': ('models.CharField', ['_(u"Shipping phone")'], {'max_length': '20', 'blank': 'True'}),
            'shipping_price': ('models.FloatField', ['_(u"Shipping Price")'], {'default': '0.0'}),
            'shipping_street': ('models.CharField', ['_(u"Shipping street")'], {'max_length': '100', 'blank': 'True'}),
            'shipping_tax': ('models.FloatField', ['_(u"Shipping Tax")'], {'default': '0.0'}),
            'shipping_zip_code': ('models.CharField', ['_(u"Shipping zip code")'], {'max_length': '10'}),
            'state': ('models.PositiveSmallIntegerField', ['_(u"State")'], {'default': 'SUBMITTED'}),
            'tax': ('models.FloatField', ['_(u"Tax")'], {'default': '0.0'}),
            'user': ('models.ForeignKey', ['User'], {'null': 'True', 'verbose_name': '_(u"User")', 'blank': 'True'})
        },
        'payment.paymentmethod': {
            'Meta': {'ordering': '("priority",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.country': {
            'Meta': {'ordering': '("name",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['order']
