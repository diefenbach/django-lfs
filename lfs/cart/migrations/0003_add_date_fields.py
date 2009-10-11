
from south.db import db
from django.db import models
from lfs.cart.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'CartItem.creation_date'
        db.add_column('cart_cartitem', 'creation_date', models.DateTimeField(_(u"Creation date"), auto_now_add=True))
        
        # Adding field 'Cart.creation_date'
        db.add_column('cart_cart', 'creation_date', models.DateTimeField(_(u"Creation date"), auto_now_add=True))
        
        # Adding field 'CartItem.modification_date'
        db.add_column('cart_cartitem', 'modification_date', models.DateTimeField(_(u"Modification date"), auto_now=True, auto_now_add=True))
        
        # Adding field 'Cart.modification_date'
        db.add_column('cart_cart', 'modification_date', models.DateTimeField(_(u"Modification date"), auto_now=True, auto_now_add=True))
        
    def backwards(self, orm):
        
        # Deleting field 'CartItem.creation_date'
        db.delete_column('cart_cartitem', 'creation_date')
        
        # Deleting field 'Cart.creation_date'
        db.delete_column('cart_cart', 'creation_date')
        
        # Deleting field 'CartItem.modification_date'
        db.delete_column('cart_cartitem', 'modification_date')
        
        # Deleting field 'Cart.modification_date'
        db.delete_column('cart_cart', 'modification_date')
            
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
            'cart': ('models.ForeignKey', ["orm['cart.Cart']"], {}),
            'creation_date': ('models.DateTimeField', ['_(u"Creation date")'], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'modification_date': ('models.DateTimeField', ['_(u"Modification date")'], {'auto_now': 'True', 'auto_now_add': 'True'}),
            'product': ('models.ForeignKey', ["orm['catalog.Product']"], {})
        },
        'cart.cart': {
            'creation_date': ('models.DateTimeField', ['_(u"Creation date")'], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'modification_date': ('models.DateTimeField', ['_(u"Modification date")'], {'auto_now': 'True', 'auto_now_add': 'True'}),
            'session': ('models.CharField', ['_(u"Session")'], {'max_length': '100', 'blank': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['cart']
