
from south.db import db
from django.db import models
from lfs.criteria.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'PaymentMethodCriterion'
        db.create_table('criteria_paymentmethodcriterion', (
            ('id', models.AutoField(primary_key=True)),
            ('operator', models.PositiveIntegerField(_(u"Operator"), null=True, blank=True)),
        ))
        db.send_create_signal('criteria', ['PaymentMethodCriterion'])
        
        # Adding ManyToManyField 'PaymentMethodCriterion.payment_methods'
        db.create_table('criteria_paymentmethodcriterion_payment_methods', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('paymentmethodcriterion', models.ForeignKey(orm.PaymentMethodCriterion, null=False)),
            ('paymentmethod', models.ForeignKey(orm['payment.PaymentMethod'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'PaymentMethodCriterion'
        db.delete_table('criteria_paymentmethodcriterion')
        
        # Dropping ManyToManyField 'PaymentMethodCriterion.payment_methods'
        db.delete_table('criteria_paymentmethodcriterion_payment_methods')
        
    
    
    models = {
        'criteria.weightcriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'}),
            'weight': ('models.FloatField', ['_(u"Weight")'], {'default': '0.0'})
        },
        'criteria.combinedlengthandgirthcriterion': {
            'clag': ('models.FloatField', ['_(u"Width")'], {'default': '0.0'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'})
        },
        'payment.paymentmethod': {
            'Meta': {'ordering': '("priority",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'criteria.heightcriterion': {
            'height': ('models.FloatField', ['_(u"Height")'], {'default': '0.0'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'criteria.criteriaobjects': {
            'Meta': {'ordering': '["position"]', 'app_label': '"criteria"'},
            'content_id': ('models.PositiveIntegerField', ['_(u"Content id")'], {}),
            'content_type': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': '"content_type"'}),
            'criterion_id': ('models.PositiveIntegerField', ['_(u"Content id")'], {}),
            'criterion_type': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': '"criterion"'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.PositiveIntegerField', ['_(u"Position")'], {'default': '999'})
        },
        'criteria.usercriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'users': ('models.ManyToManyField', ["orm['auth.User']"], {})
        },
        'criteria.countrycriterion': {
            'countries': ('models.ManyToManyField', ["orm['core.Country']"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'criteria.lengthcriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'length': ('models.FloatField', ['_(u"Length")'], {'default': '0.0'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'})
        },
        'core.country': {
            'Meta': {'ordering': '("name",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'criteria.paymentmethodcriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'}),
            'payment_methods': ('models.ManyToManyField', ["orm['payment.PaymentMethod']"], {})
        },
        'criteria.widthcriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'}),
            'width': ('models.FloatField', ['_(u"Width")'], {'default': '0.0'})
        },
        'criteria.cartpricecriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'})
        }
    }
    
    complete_apps = ['criteria']
