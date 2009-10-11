
from south.db import db
from django.db import models
from lfs.page.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Page'
        db.create_table('page_page', (
            ('body', models.TextField(_(u"Text"), blank=True)),
            ('title', models.CharField(_(u"Title"), max_length=100)),
            ('id', models.AutoField(primary_key=True)),
            ('file', models.FileField(_(u"File"), upload_to="files", blank=True)),
            ('active', models.BooleanField(_(u"Active"), default=False)),
            ('position', models.IntegerField(_(u"Position"), default=999)),
            ('short_text', models.TextField(blank=True)),
            ('slug', models.CharField(_(u"Slug"), max_length=100)),
        ))
        db.send_create_signal('page', ['Page'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Page'
        db.delete_table('page_page')
        
    
    
    models = {
        'page.page': {
            'Meta': {'ordering': '("position",)'},
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'body': ('models.TextField', ['_(u"Text")'], {'blank': 'True'}),
            'file': ('models.FileField', ['_(u"File")'], {'upload_to': '"files"', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '999'}),
            'short_text': ('models.TextField', [], {'blank': 'True'}),
            'slug': ('models.CharField', ['_(u"Slug")'], {'max_length': '100'}),
            'title': ('models.CharField', ['_(u"Title")'], {'max_length': '100'})
        }
    }
    
    complete_apps = ['page']
