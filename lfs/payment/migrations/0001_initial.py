
from south.db import db
from django.db import models
from lfs.payment.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'PaymentMethod'
        db.create_table('payment_paymentmethod', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_(u"Name"), max_length=50, blank=True)),
            ('active', models.BooleanField(_(u"Active"), default=False)),
            ('description', models.TextField(_(u"Description"), blank=True)),
            ('note', models.TextField(_(u"note"), blank=True)),
            ('priority', models.IntegerField(_(u"Priority"), default=0)),
            ('image', models.ImageField(_(u"Image"), null=True, blank=True)),
            ('tax', models.ForeignKey(orm['tax.Tax'], null=True, verbose_name=_(u"Tax"), blank=True)),
            ('price', models.FloatField(_(u"Price"), default=0.0)),
            ('deletable', models.BooleanField(default=True)),
        ))
        db.send_create_signal('payment', ['PaymentMethod'])
        
        # Adding model 'PaymentMethodPrice'
        db.create_table('payment_paymentmethodprice', (
            ('id', models.AutoField(primary_key=True)),
            ('payment_method', models.ForeignKey(orm.PaymentMethod, related_name="prices", verbose_name=_(u"Payment method"))),
            ('price', models.FloatField(_(u"Price"), default=0.0)),
            ('priority', models.IntegerField(_(u"Priority"), default=0)),
            ('active', models.BooleanField(_(u"Active"), default=False)),
        ))
        db.send_create_signal('payment', ['PaymentMethodPrice'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'PaymentMethod'
        db.delete_table('payment_paymentmethod')
        
        # Deleting model 'PaymentMethodPrice'
        db.delete_table('payment_paymentmethodprice')
        
    
    
    models = {
        'payment.paymentmethod': {
            'Meta': {'ordering': '("priority",)'},
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'deletable': ('models.BooleanField', [], {'default': 'True'}),
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ImageField', ['_(u"Image")'], {'null': 'True', 'blank': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '50', 'blank': 'True'}),
            'note': ('models.TextField', ['_(u"note")'], {'blank': 'True'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'}),
            'priority': ('models.IntegerField', ['_(u"Priority")'], {'default': '0'}),
            'tax': ('models.ForeignKey', ["orm['tax.Tax']"], {'null': 'True', 'verbose_name': '_(u"Tax")', 'blank': 'True'})
        },
        'tax.tax': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'payment.paymentmethodprice': {
            'Meta': {'ordering': '("priority",)'},
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'payment_method': ('models.ForeignKey', ["orm['payment.PaymentMethod']"], {'related_name': '"prices"', 'verbose_name': '_(u"Payment method")'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'}),
            'priority': ('models.IntegerField', ['_(u"Priority")'], {'default': '0'})
        }
    }
    
    complete_apps = ['payment']
