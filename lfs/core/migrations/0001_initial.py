
from south.db import db
from django.db import models
from lfs.core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Action'
        db.create_table('core_action', (
            ('parent', models.ForeignKey(orm.Action, null=True, verbose_name=_(u"Parent"), blank=True)),
            ('title', models.CharField(_(u"Title"), max_length=40)),
            ('place', models.PositiveSmallIntegerField(default=ACTION_PLACE_TABS, null=True, blank=True)),
            ('active', models.BooleanField(_(u"Active"), default=False)),
            ('position', models.IntegerField(_(u"Position"), default=999)),
            ('id', models.AutoField(primary_key=True)),
            ('link', models.CharField(_(u"Link"), max_length=100, blank=True)),
        ))
        db.send_create_signal('core', ['Action'])
        
        # Adding model 'Shop'
        db.create_table('core_shop', (
            ('static_block', models.ForeignKey(orm['catalog.StaticBlock'], related_name="shops", null=True, verbose_name=_(u"Static block"), blank=True)),
            ('google_analytics_id', models.CharField(_(u"Google Analytics ID"), max_length=20, blank=True)),
            ('description', models.TextField(_(u"Description"), blank=True)),
            ('ga_ecommerce_tracking', models.BooleanField(_(u"Google Analytics E-Commerce Tracking"), default=False)),
            ('image', ImageWithThumbsField(_(u"Image"), null=True, upload_to="images", sizes=((60,60),(100,100),(200,200),(400,400)), blank=True)),
            ('checkout_type', models.PositiveSmallIntegerField(_(u"Checkout type"), default=CHECKOUT_TYPE_SELECT)),
            ('from_email', models.EmailField(_(u"From e-mail address"))),
            ('default_country', models.ForeignKey(orm.Country, verbose_name=_(u"Default country"))),
            ('product_cols', models.IntegerField(_(u"Product cols"), default=3)),
            ('category_cols', models.IntegerField(_(u"Category cols"), default=3)),
            ('notification_emails', models.TextField(_(u"Notification email addresses"))),
            ('shop_owner', models.CharField(_(u"Shop owner"), max_length=100, blank=True)),
            ('product_rows', models.IntegerField(_(u"Product rows"), default=3)),
            ('id', models.AutoField(primary_key=True)),
            ('ga_site_tracking', models.BooleanField(_(u"Google Analytics Site Tracking"), default=False)),
            ('name', models.CharField(_(u"Name"), max_length=30)),
        ))
        db.send_create_signal('core', ['Shop'])
        
        # Adding model 'Country'
        db.create_table('core_country', (
            ('code', models.CharField(_(u"Country code"), max_length=2)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_(u"Name"), max_length=100)),
        ))
        db.send_create_signal('core', ['Country'])
        
        # Adding ManyToManyField 'Shop.countries'
        db.create_table('core_shop_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shop', models.ForeignKey(Shop, null=False)),
            ('country', models.ForeignKey(Country, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Action'
        db.delete_table('core_action')
        
        # Deleting model 'Shop'
        db.delete_table('core_shop')
        
        # Deleting model 'Country'
        db.delete_table('core_country')
        
        # Dropping ManyToManyField 'Shop.countries'
        db.delete_table('core_shop_countries')
        
    
    
    models = {
        'core.action': {
            'Meta': {'ordering': '("position",)'},
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'link': ('models.CharField', ['_(u"Link")'], {'max_length': '100', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ['"self"'], {'null': 'True', 'verbose_name': '_(u"Parent")', 'blank': 'True'}),
            'place': ('models.PositiveSmallIntegerField', [], {'default': 'ACTION_PLACE_TABS', 'null': 'True', 'blank': 'True'}),
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
            'checkout_type': ('models.PositiveSmallIntegerField', ['_(u"Checkout type")'], {'default': 'CHECKOUT_TYPE_SELECT'}),
            'countries': ('models.ManyToManyField', ['Country'], {'related_name': '"shops"', 'verbose_name': '_(u"Countries")'}),
            'default_country': ('models.ForeignKey', ['Country'], {'verbose_name': '_(u"Default country")'}),
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'from_email': ('models.EmailField', ['_(u"From e-mail address")'], {}),
            'ga_ecommerce_tracking': ('models.BooleanField', ['_(u"Google Analytics E-Commerce Tracking")'], {'default': 'False'}),
            'ga_site_tracking': ('models.BooleanField', ['_(u"Google Analytics Site Tracking")'], {'default': 'False'}),
            'google_analytics_id': ('models.CharField', ['_(u"Google Analytics ID")'], {'max_length': '20', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('ImageWithThumbsField', ['_(u"Image")'], {'null': 'True', 'upload_to': '"images"', 'sizes': '((60,60),(100,100),(200,200),(400,400))', 'blank': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '30'}),
            'notification_emails': ('models.TextField', ['_(u"Notification email addresses")'], {}),
            'product_cols': ('models.IntegerField', ['_(u"Product cols")'], {'default': '3'}),
            'product_rows': ('models.IntegerField', ['_(u"Product rows")'], {'default': '3'}),
            'shop_owner': ('models.CharField', ['_(u"Shop owner")'], {'max_length': '100', 'blank': 'True'}),
            'static_block': ('models.ForeignKey', ['StaticBlock'], {'related_name': '"shops"', 'null': 'True', 'verbose_name': '_(u"Static block")', 'blank': 'True'})
        },
        'core.country': {
            'Meta': {'ordering': '("name",)'},
            'code': ('models.CharField', ['_(u"Country code")'], {'max_length': '2'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '100'})
        }
    }
    
    complete_apps = ['core']
