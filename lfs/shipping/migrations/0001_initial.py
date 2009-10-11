
from south.db import db
from django.db import models
from lfs.shipping.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'ShippingMethodPrice'
        db.create_table('shipping_shippingmethodprice', (
            ('id', models.AutoField(primary_key=True)),
            ('shipping_method', models.ForeignKey(orm.ShippingMethod, related_name="prices", verbose_name=_(u"shipping_method"))),
            ('price', models.FloatField(_(u"Price"), default=0.0)),
            ('priority', models.IntegerField(_(u"Priority"), default=0)),
            ('active', models.BooleanField(_(u"Active"), default=True)),
        ))
        db.send_create_signal('shipping', ['ShippingMethodPrice'])
        
        # Adding model 'ShippingMethod'
        db.create_table('shipping_shippingmethod', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_(u"Name"), max_length=50)),
            ('description', models.TextField(_(u"Description"), blank=True)),
            ('note', models.TextField(_(u"Note"), blank=True)),
            ('priority', models.IntegerField(_(u"Priority"), default=0)),
            ('image', models.ImageField(_(u"Image"), null=True, blank=True)),
            ('active', models.BooleanField(_(u"Active"), default=False)),
            ('tax', models.ForeignKey(orm['tax.Tax'], null=True, verbose_name=_(u"Tax"), blank=True)),
            ('price', models.FloatField(_(u"Price"), default=0.0)),
            ('delivery_time', models.ForeignKey(orm['catalog.DeliveryTime'], null=True, verbose_name=_(u"Delivery time"), blank=True)),
        ))
        db.send_create_signal('shipping', ['ShippingMethod'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'ShippingMethodPrice'
        db.delete_table('shipping_shippingmethodprice')
        
        # Deleting model 'ShippingMethod'
        db.delete_table('shipping_shippingmethod')
        
    
    
    models = {
        'shipping.shippingmethodprice': {
            'Meta': {'ordering': '("priority",)'},
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'}),
            'priority': ('models.IntegerField', ['_(u"Priority")'], {'default': '0'}),
            'shipping_method': ('models.ForeignKey', ["orm['shipping.ShippingMethod']"], {'related_name': '"prices"', 'verbose_name': '_(u"shipping_method")'})
        },
        'catalog.deliverytime': {
            'Meta': {'ordering': '("min",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'tax.tax': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'shipping.shippingmethod': {
            'Meta': {'ordering': '("priority",)'},
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'delivery_time': ('models.ForeignKey', ["orm['catalog.DeliveryTime']"], {'null': 'True', 'verbose_name': '_(u"Delivery time")', 'blank': 'True'}),
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ImageField', ['_(u"Image")'], {'null': 'True', 'blank': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '50'}),
            'note': ('models.TextField', ['_(u"Note")'], {'blank': 'True'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'}),
            'priority': ('models.IntegerField', ['_(u"Priority")'], {'default': '0'}),
            'tax': ('models.ForeignKey', ["orm['tax.Tax']"], {'null': 'True', 'verbose_name': '_(u"Tax")', 'blank': 'True'})
        }
    }
    
    complete_apps = ['shipping']
