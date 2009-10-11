
from south.db import db
from django.db import models
from lfs.core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Shop.default_currency'
        db.add_column('core_shop', 'default_currency', models.CharField(_(u"Default Currency"), default='EUR', max_length=30))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Shop.default_currency'
        db.delete_column('core_shop', 'default_currency')
        
    
    
    models = {
        'core.action': {
            'Meta': {'ordering': '("position",)'},
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'link': ('models.CharField', ['_(u"Link")'], {'max_length': '100', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ["orm['core.Action']"], {'null': 'True', 'blank': 'True'}),
            'place': ('models.PositiveSmallIntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '999'}),
            'title': ('models.CharField', ['_(u"Title")'], {'max_length': '40'})
        },
        'catalog.staticblock': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.shop': {
            'Meta': {'permissions': '(("manage_shop","Manage shop"),)'},
            'category_cols': ('models.IntegerField', ['_(u"Category cols")'], {'default': '3'}),
            'checkout_type': ('models.PositiveSmallIntegerField', ['_(u"Checkout type")'], {'default': '0'}),
            'countries': ('models.ManyToManyField', ["orm['core.Country']"], {'related_name': '"shops"'}),
            'default_country': ('models.ForeignKey', ["orm['core.Country']"], {}),
            'default_currency': ('models.CharField', ['_(u"Default Currency")'], {'default': "'EUR'", 'max_length': '30'}),
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'from_email': ('models.EmailField', ['_(u"From e-mail address")'], {}),
            'ga_ecommerce_tracking': ('models.BooleanField', ['_(u"Google Analytics E-Commerce Tracking")'], {'default': 'False'}),
            'ga_site_tracking': ('models.BooleanField', ['_(u"Google Analytics Site Tracking")'], {'default': 'False'}),
            'google_analytics_id': ('models.CharField', ['_(u"Google Analytics ID")'], {'max_length': '20', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('ImageWithThumbsField', ['_(u"Image")'], {'null': 'True', 'sizes': '((60,60),(100,100),(200,200),(400,400))', 'blank': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '30'}),
            'notification_emails': ('models.TextField', ['_(u"Notification email addresses")'], {}),
            'product_cols': ('models.IntegerField', ['_(u"Product cols")'], {'default': '3'}),
            'product_rows': ('models.IntegerField', ['_(u"Product rows")'], {'default': '3'}),
            'shop_owner': ('models.CharField', ['_(u"Shop owner")'], {'max_length': '100', 'blank': 'True'}),
            'static_block': ('models.ForeignKey', ["orm['catalog.StaticBlock']"], {'related_name': '"shops"', 'null': 'True', 'blank': 'True'})
        },
        'core.country': {
            'Meta': {'ordering': '("name",)'},
            'code': ('models.CharField', ['_(u"Country code")'], {'max_length': '2'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '100'})
        }
    }
    
    complete_apps = ['core']
