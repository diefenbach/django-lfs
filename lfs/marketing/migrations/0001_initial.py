
from south.db import db
from django.db import models
from lfs.marketing.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Topseller'
        db.create_table('marketing_topseller', (
            ('position', models.PositiveSmallIntegerField(_(u"Position"), default=1)),
            ('product', models.ForeignKey(orm['catalog.Product'], verbose_name=_(u"Product"))),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('marketing', ['Topseller'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Topseller'
        db.delete_table('marketing_topseller')
        
    
    
    models = {
        'marketing.topseller': {
            'Meta': {'ordering': '["position"]'},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.PositiveSmallIntegerField', ['_(u"Position")'], {'default': '1'}),
            'product': ('models.ForeignKey', ['Product'], {'verbose_name': '_(u"Product")'})
        },
        'catalog.product': {
            'Meta': {'ordering': '("name",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['marketing']
