
from south.db import db
from django.db import models
from lfs.cart.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'CartItem'
        db.create_table('cart_cartitem', (
            ('amount', models.IntegerField(_(u"Quantity"), null=True, blank=True)),
            ('product', models.ForeignKey(orm['catalog.Product'], verbose_name=_(u"Product"))),
            ('id', models.AutoField(primary_key=True)),
            ('cart', models.ForeignKey(orm.Cart, verbose_name=_(u"Cart"))),
        ))
        db.send_create_signal('cart', ['CartItem'])
        
        # Adding model 'Cart'
        db.create_table('cart_cart', (
            ('session', models.CharField(_(u"Session"), max_length=100, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm['auth.User'], null=True, verbose_name=_(u"User"), blank=True)),
        ))
        db.send_create_signal('cart', ['Cart'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'CartItem'
        db.delete_table('cart_cartitem')
        
        # Deleting model 'Cart'
        db.delete_table('cart_cart')
        
    
    
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
            'cart': ('models.ForeignKey', ['Cart'], {'verbose_name': '_(u"Cart")'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'product': ('models.ForeignKey', ['Product'], {'verbose_name': '_(u"Product")'})
        },
        'cart.cart': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'session': ('models.CharField', ['_(u"Session")'], {'max_length': '100', 'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'null': 'True', 'verbose_name': '_(u"User")', 'blank': 'True'})
        }
    }
    
    complete_apps = ['cart']
