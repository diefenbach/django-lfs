
from south.db import db
from django.db import models
from lfs.tax.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Tax'
        db.create_table('tax_tax', (
            ('rate', models.FloatField(_(u"Rate"), default=0)),
            ('id', models.AutoField(primary_key=True)),
            ('description', models.TextField(_(u"Description"), blank=True)),
        ))
        db.send_create_signal('tax', ['Tax'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Tax'
        db.delete_table('tax_tax')
        
    
    
    models = {
        'tax.tax': {
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'rate': ('models.FloatField', ['_(u"Rate")'], {'default': '0'})
        }
    }
    
    complete_apps = ['tax']
