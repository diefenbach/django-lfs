
from south.db import db
from django.db import models
from lfs.catalog.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Product.variant_position'
        db.add_column('catalog_product', 'variant_position', models.IntegerField(default=999))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Product.variant_position'
        db.delete_column('catalog_product', 'variant_position')
        
    
    
    models = {
        'catalog.productpropertyvalue': {
            'Meta': {'unique_together': '("product","property","value")'},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product': ('models.ForeignKey', ["orm['catalog.Product']"], {'related_name': '"property_values"'}),
            'property': ('models.ForeignKey', ["orm['catalog.Property']"], {'related_name': '"property_values"'}),
            'value': ('models.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'value_as_float': ('models.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'catalog.staticblock': {
            'html': ('models.TextField', ['_(u"HTML")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '30'})
        },
        'catalog.propertygroup': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'products': ('models.ManyToManyField', ["orm['catalog.Product']"], {'related_name': '"property_groups"'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'catalog.category': {
            'Meta': {'ordering': '("position",)'},
            'active_formats': ('models.BooleanField', ['_(u"Active formats")'], {'default': 'False'}),
            'category_cols': ('models.IntegerField', ['_(u"Category cols")'], {'default': '3'}),
            'content': ('models.IntegerField', ['_(u"Content")'], {'default': '1'}),
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'exclude_from_navigation': ('models.BooleanField', ['_(u"Exclude from navigation")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('ImageWithThumbsField', ['_(u"Image")'], {'null': 'True', 'sizes': '((60,60),(100,100),(200,200),(400,400))', 'blank': 'True'}),
            'meta_description': ('models.TextField', ['_(u"Meta description")'], {'blank': 'True'}),
            'meta_keywords': ('models.TextField', ['_(u"Meta keywords")'], {'blank': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '50'}),
            'parent': ('models.ForeignKey', ["orm['catalog.Category']"], {'null': 'True', 'blank': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '1000'}),
            'product_cols': ('models.IntegerField', ['_(u"Product cols")'], {'default': '3'}),
            'product_rows': ('models.IntegerField', ['_(u"Product rows")'], {'default': '3'}),
            'products': ('models.ManyToManyField', ["orm['catalog.Product']"], {'related_name': '"categories"', 'blank': 'True'}),
            'short_description': ('models.TextField', ['_(u"Short description")'], {'blank': 'True'}),
            'show_all_products': ('models.BooleanField', ['_(u"Show all products")'], {'default': 'True'}),
            'slug': ('models.SlugField', ['_(u"Slug")'], {'unique': 'True'}),
            'static_block': ('models.ForeignKey', ["orm['catalog.StaticBlock']"], {'related_name': '"categories"', 'null': 'True', 'blank': 'True'}),
            'uid': ('models.CharField', [], {'max_length': '50'})
        },
        'catalog.productaccessories': {
            'Meta': {'ordering': '("position",)'},
            'accessory': ('models.ForeignKey', ["orm['catalog.Product']"], {'related_name': '"productaccessories_accessory"'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '999'}),
            'product': ('models.ForeignKey', ["orm['catalog.Product']"], {'related_name': '"productaccessories_product"'}),
            'quantity': ('models.FloatField', ['_(u"Quantity")'], {'default': '1'})
        },
        'catalog.filterstep': {
            'Meta': {'ordering': '["start"]'},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'property': ('models.ForeignKey', ["orm['catalog.Property']"], {'related_name': '"steps"'}),
            'start': ('models.FloatField', [], {})
        },
        'catalog.product': {
            'Meta': {'ordering': '("name",)'},
            'accessories': ('models.ManyToManyField', ["orm['catalog.Product']"], {'related_name': '"reverse_accessories"', 'through': '"ProductAccessories"', 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'active_accessories': ('models.BooleanField', ['_(u"Active accessories")'], {'default': 'False'}),
            'active_description': ('models.BooleanField', ['_(u"Active description")'], {'default': 'False'}),
            'active_dimensions': ('models.BooleanField', ['_(u"Active dimensions")'], {'default': 'False'}),
            'active_for_sale': ('models.PositiveSmallIntegerField', ['_("Active for sale")'], {'default': '0'}),
            'active_for_sale_price': ('models.BooleanField', ['_(u"Active for sale price")'], {'default': 'False'}),
            'active_images': ('models.BooleanField', ['_(u"Active Images")'], {'default': 'False'}),
            'active_meta_description': ('models.BooleanField', ['_(u"Active meta description")'], {'default': 'False'}),
            'active_meta_keywords': ('models.BooleanField', ['_(u"Active meta keywords")'], {'default': 'False'}),
            'active_name': ('models.BooleanField', ['_(u"Active name")'], {'default': 'False'}),
            'active_price': ('models.BooleanField', ['_(u"Active price")'], {'default': 'False'}),
            'active_related_products': ('models.BooleanField', ['_(u"Active related products")'], {'default': 'False'}),
            'active_short_description': ('models.BooleanField', ['_(u"Active short description")'], {'default': 'False'}),
            'active_sku': ('models.BooleanField', ['_(u"Active SKU")'], {'default': 'False'}),
            'creation_date': ('models.DateTimeField', ['_(u"Creation date")'], {'auto_now_add': 'True'}),
            'default_variant': ('models.ForeignKey', ["orm['catalog.Product']"], {'null': 'True', 'blank': 'True'}),
            'deliverable': ('models.BooleanField', ['_(u"Deliverable")'], {'default': 'True'}),
            'delivery_time': ('models.ForeignKey', ["orm['catalog.DeliveryTime']"], {'related_name': '"products_delivery_time"', 'null': 'True', 'blank': 'True'}),
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'effective_price': ('models.FloatField', ['_(u"Price")'], {'blank': 'True'}),
            'for_sale': ('models.BooleanField', ['_(u"For sale")'], {'default': 'False'}),
            'for_sale_price': ('models.FloatField', ['_(u"For sale price")'], {'default': '0.0'}),
            'height': ('models.FloatField', ['_(u"Height")'], {'default': '0.0'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'images': ('generic.GenericRelation', ["orm['catalog.Image']"], {'object_id_field': '"content_id"', 'content_type_field': '"content_type"'}),
            'length': ('models.FloatField', ['_(u"Length")'], {'default': '0.0'}),
            'manage_stock_amount': ('models.BooleanField', ['_(u"Manage stock amount")'], {'default': 'True'}),
            'manual_delivery_time': ('models.BooleanField', ['_(u"Manual delivery time")'], {'default': 'False'}),
            'meta_description': ('models.TextField', ['_(u"Meta description")'], {'blank': 'True'}),
            'meta_keywords': ('models.TextField', ['_(u"Meta keywords")'], {'blank': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '80', 'blank': 'True'}),
            'order_time': ('models.ForeignKey', ["orm['catalog.DeliveryTime']"], {'related_name': '"products_order_time"', 'null': 'True', 'blank': 'True'}),
            'ordered_at': ('models.DateField', ['_(u"Ordered at")'], {'null': 'True', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ["orm['catalog.Product']"], {'related_name': '"variants"', 'null': 'True', 'blank': 'True'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'}),
            'related_products': ('models.ManyToManyField', ["orm['catalog.Product']"], {'related_name': '"reverse_related_products"', 'symmetrical': 'False', 'null': 'True', 'blank': 'True'}),
            'short_description': ('models.TextField', ['_(u"Short description")'], {'blank': 'True'}),
            'sku': ('models.CharField', ['_(u"SKU")'], {'max_length': '30', 'blank': 'True'}),
            'slug': ('models.SlugField', ['_(u"Slug")'], {'max_length': '80', 'unique': 'True'}),
            'stock_amount': ('models.FloatField', ['_(u"Stock amount")'], {'default': '0'}),
            'sub_type': ('models.CharField', ['_(u"Subtype")'], {'default': "'0'", 'max_length': '10'}),
            'tax': ('models.ForeignKey', ["orm['tax.Tax']"], {'null': 'True', 'blank': 'True'}),
            'uid': ('models.CharField', [], {'max_length': '50'}),
            'variant_position': ('models.IntegerField', [], {'default': '999'}),
            'variants_display_type': ('models.IntegerField', ['_(u"Variants display type")'], {'default': '0'}),
            'weight': ('models.FloatField', ['_(u"Weight")'], {'default': '0.0'}),
            'width': ('models.FloatField', ['_(u"Width")'], {'default': '0.0'})
        },
        'catalog.deliverytime': {
            'Meta': {'ordering': '("min",)'},
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'max': ('models.FloatField', ['_(u"Max")'], {}),
            'min': ('models.FloatField', ['_(u"Min")'], {}),
            'unit': ('models.PositiveSmallIntegerField', ['_(u"Unit")'], {'default': '2'})
        },
        'catalog.propertyoption': {
            'Meta': {'ordering': '["position"]'},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '100'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '99'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'property': ('models.ForeignKey', ["orm['catalog.Property']"], {'related_name': '"options"'}),
            'uid': ('models.CharField', [], {'max_length': '50'})
        },
        'catalog.productspropertiesrelation': {
            'Meta': {'ordering': '("position",)', 'unique_together': '("product","property")'},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '999'}),
            'product': ('models.ForeignKey', ["orm['catalog.Product']"], {'related_name': '"productsproperties"'}),
            'property': ('models.ForeignKey', ["orm['catalog.Property']"], {})
        },
        'catalog.image': {
            'Meta': {'ordering': '("position",)'},
            'content_id': ('models.PositiveIntegerField', ['_(u"Content id")'], {'null': 'True', 'blank': 'True'}),
            'content_type': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': '"image"', 'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('ImageWithThumbsField', ['_(u"Image")'], {'null': 'True', 'sizes': '((60,60),(100,100),(200,200),(400,400))', 'blank': 'True'}),
            'position': ('models.PositiveSmallIntegerField', ['_(u"Position")'], {'default': '999'}),
            'title': ('models.CharField', ['_(u"Title")'], {'max_length': '100', 'blank': 'True'})
        },
        'catalog.groupspropertiesrelation': {
            'Meta': {'ordering': '("position",)', 'unique_together': '("group","property")'},
            'group': ('models.ForeignKey', ["orm['catalog.PropertyGroup']"], {'related_name': '"groupproperties"'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '999'}),
            'property': ('models.ForeignKey', ["orm['catalog.Property']"], {})
        },
        'tax.tax': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'catalog.property': {
            'Meta': {'ordering': '["position"]'},
            'display_no_results': ('models.BooleanField', ['_(u"Display no results")'], {'default': 'False'}),
            'display_on_product': ('models.BooleanField', ['_(u"Display on product")'], {'default': 'True'}),
            'filterable': ('models.BooleanField', [], {'default': 'True'}),
            'groups': ('models.ManyToManyField', ["orm['catalog.PropertyGroup']"], {'related_name': '"properties"', 'through': '"GroupsPropertiesRelation"', 'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'local': ('models.BooleanField', [], {'default': 'False'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '100'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'null': 'True', 'blank': 'True'}),
            'products': ('models.ManyToManyField', ["orm['catalog.Product']"], {'related_name': '"properties"', 'through': '"ProductsPropertiesRelation"', 'null': 'True', 'blank': 'True'}),
            'step': ('models.IntegerField', ['_(u"Step")'], {'null': 'True', 'blank': 'True'}),
            'step_type': ('models.PositiveSmallIntegerField', ['_(u"Step type")'], {'default': '1'}),
            'type': ('models.PositiveSmallIntegerField', ['_(u"Type")'], {'default': '2'}),
            'uid': ('models.CharField', [], {'max_length': '50'}),
            'unit': ('models.CharField', ['_(u"Unit")'], {'max_length': '15', 'blank': 'True'})
        }
    }
    
    complete_apps = ['catalog']
