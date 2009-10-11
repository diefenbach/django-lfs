
from south.db import db
from django.db import models
from lfs.payment.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'PayPalOrderTransaction'
        db.create_table('payment_paypalordertransaction', (
            ('id', models.AutoField(primary_key=True)),
            ('order', models.ForeignKey(orm['order.Order'], unique=True)),
        ))
        db.send_create_signal('payment', ['PayPalOrderTransaction'])
        
        # Adding ManyToManyField 'PayPalOrderTransaction.ipn'
        db.create_table('payment_paypalordertransaction_ipn', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('paypalordertransaction', models.ForeignKey(orm.PayPalOrderTransaction, null=False)),
            ('paypalipn', models.ForeignKey(orm['ipn.PayPalIPN'], null=False))
        ))
    
    def backwards(self, orm):
        
        # Deleting model 'PayPalOrderTransaction'
        db.delete_table('payment_paypalordertransaction')
        
        # Dropping ManyToManyField 'PayPalOrderTransaction.ipn'
        db.delete_table('payment_paypalordertransaction_ipn')
            
    models = {
        'ipn.paypalipn': {
            'Meta': {'db_table': '"paypal_ipn"'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'payment.paypalordertransaction': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('models.ManyToManyField', ["orm['ipn.PayPalIPN']"], {}),
            'order': ('models.ForeignKey', ["orm['order.Order']"], {'unique': 'True'})
        },
        'payment.paymentmethod': {
            'Meta': {'ordering': '("priority",)'},
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'criteria_objects': ('generic.GenericRelation', ["orm['criteria.CriteriaObjects']"], {'object_id_field': '"content_id"', 'content_type_field': '"content_type"'}),
            'deletable': ('models.BooleanField', [], {'default': 'True'}),
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ImageField', ['_(u"Image")'], {'null': 'True', 'blank': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '50', 'blank': 'True'}),
            'note': ('models.TextField', ['_(u"note")'], {'blank': 'True'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'}),
            'priority': ('models.IntegerField', ['_(u"Priority")'], {'default': '0'}),
            'tax': ('models.ForeignKey', ["orm['tax.Tax']"], {'null': 'True', 'blank': 'True'})
        },
        'order.order': {
            'Meta': {'ordering': '("-created",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'tax.tax': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'criteria.criteriaobjects': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'payment.paymentmethodprice': {
            'Meta': {'ordering': '("priority",)'},
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'criteria_objects': ('generic.GenericRelation', ["orm['criteria.CriteriaObjects']"], {'object_id_field': '"content_id"', 'content_type_field': '"content_type"'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'payment_method': ('models.ForeignKey', ["orm['payment.PaymentMethod']"], {'related_name': '"prices"'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'}),
            'priority': ('models.IntegerField', ['_(u"Priority")'], {'default': '0'})
        }
    }
    
    complete_apps = ['payment']
