
from south.db import db
from django.db import models
from lfs.cart.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'CartPortlet'
        db.create_table('cart_cartportlet', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_(u"Title"), max_length=50, blank=True)),
        ))
        db.send_create_signal('cart', ['CartPortlet'])
        
    def backwards(self, orm):
        
        # Deleting model 'CartPortlet'
        db.delete_table('cart_cartportlet')
        
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'catalog.product': {
            'Meta': {'ordering': '("name",)'},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'cart.cartitem': {
            'Meta': {'ordering': "['id']"},
            'amount': ('models.IntegerField', ['_(u"Quantity")'], {'null': 'True', 'blank': 'True'}),
            'cart': ('models.ForeignKey', ["orm['cart.Cart']"], {'verbose_name': '_(u"Cart")'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'product': ('models.ForeignKey', ["orm['catalog.Product']"], {'verbose_name': '_(u"Product")'})
        },
        'cart.cart': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'session': ('models.CharField', ['_(u"Session")'], {'max_length': '100', 'blank': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': '_(u"User")', 'blank': 'True'})
        },
        'cart.cartportlet': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', ['_(u"Title")'], {'max_length': '50', 'blank': 'True'})
        }
    }
    
    complete_apps = ['cart']
