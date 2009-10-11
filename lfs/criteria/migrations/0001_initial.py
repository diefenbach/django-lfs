
from south.db import db
from django.db import models
from lfs.criteria.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'WeightCriterion'
        db.create_table('criteria_weightcriterion', (
            ('operator', models.PositiveIntegerField(_(u"Operator"), null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('weight', models.FloatField(_(u"Weight"), default=0.0)),
        ))
        db.send_create_signal('criteria', ['WeightCriterion'])
        
        # Adding model 'UserCriterion'
        db.create_table('criteria_usercriterion', (
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('criteria', ['UserCriterion'])
        
        # Adding model 'HeightCriterion'
        db.create_table('criteria_heightcriterion', (
            ('operator', models.PositiveIntegerField(null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('height', models.FloatField(_(u"Height"), default=0.0)),
        ))
        db.send_create_signal('criteria', ['HeightCriterion'])
        
        # Adding model 'CriteriaObjects'
        db.create_table('criteria_criteriaobjects', (
            ('criterion_id', models.PositiveIntegerField(_(u"Content id"))),
            ('content_type', models.ForeignKey(orm['contenttypes.ContentType'], related_name="content_type", verbose_name=_(u"Content type"))),
            ('position', models.PositiveIntegerField(_(u"Position"), default=999)),
            ('content_id', models.PositiveIntegerField(_(u"Content id"))),
            ('id', models.AutoField(primary_key=True)),
            ('criterion_type', models.ForeignKey(orm['contenttypes.ContentType'], related_name="criterion", verbose_name=_(u"Criterion type"))),
        ))
        db.send_create_signal('criteria', ['CriteriaObjects'])
        
        # Adding model 'CountryCriterion'
        db.create_table('criteria_countrycriterion', (
            ('operator', models.PositiveIntegerField(_(u"Operator"), null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('criteria', ['CountryCriterion'])
        
        # Adding model 'LengthCriterion'
        db.create_table('criteria_lengthcriterion', (
            ('operator', models.PositiveIntegerField(_(u"Operator"), null=True, blank=True)),
            ('length', models.FloatField(_(u"Length"), default=0.0)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('criteria', ['LengthCriterion'])
        
        # Adding model 'CartPriceCriterion'
        db.create_table('criteria_cartpricecriterion', (
            ('operator', models.PositiveIntegerField(_(u"Operator"), null=True, blank=True)),
            ('price', models.FloatField(_(u"Price"), default=0.0)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('criteria', ['CartPriceCriterion'])
        
        # Adding model 'WidthCriterion'
        db.create_table('criteria_widthcriterion', (
            ('operator', models.PositiveIntegerField(_(u"Operator"), null=True, blank=True)),
            ('width', models.FloatField(_(u"Width"), default=0.0)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('criteria', ['WidthCriterion'])
        
        # Adding ManyToManyField 'UserCriterion.users'
        db.create_table('criteria_usercriterion_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('usercriterion', models.ForeignKey(UserCriterion, null=False)),
            ('user', models.ForeignKey(User, null=False))
        ))
        
        # Adding ManyToManyField 'CountryCriterion.countries'
        db.create_table('criteria_countrycriterion_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('countrycriterion', models.ForeignKey(CountryCriterion, null=False)),
            ('country', models.ForeignKey(Country, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'WeightCriterion'
        db.delete_table('criteria_weightcriterion')
        
        # Deleting model 'UserCriterion'
        db.delete_table('criteria_usercriterion')
        
        # Deleting model 'HeightCriterion'
        db.delete_table('criteria_heightcriterion')
        
        # Deleting model 'CriteriaObjects'
        db.delete_table('criteria_criteriaobjects')
        
        # Deleting model 'CountryCriterion'
        db.delete_table('criteria_countrycriterion')
        
        # Deleting model 'LengthCriterion'
        db.delete_table('criteria_lengthcriterion')
        
        # Deleting model 'CartPriceCriterion'
        db.delete_table('criteria_cartpricecriterion')
        
        # Deleting model 'WidthCriterion'
        db.delete_table('criteria_widthcriterion')
        
        # Dropping ManyToManyField 'UserCriterion.users'
        db.delete_table('criteria_usercriterion_users')
        
        # Dropping ManyToManyField 'CountryCriterion.countries'
        db.delete_table('criteria_countrycriterion_countries')
        
    
    
    models = {
        'criteria.weightcriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'}),
            'weight': ('models.FloatField', ['_(u"Weight")'], {'default': '0.0'})
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
            'Meta': {'ordering': '["position"]'},
            'content_id': ('models.PositiveIntegerField', ['_(u"Content id")'], {}),
            'content_type': ('models.ForeignKey', ['ContentType'], {'related_name': '"content_type"', 'verbose_name': '_(u"Content type")'}),
            'criterion_id': ('models.PositiveIntegerField', ['_(u"Content id")'], {}),
            'criterion_type': ('models.ForeignKey', ['ContentType'], {'related_name': '"criterion"', 'verbose_name': '_(u"Criterion type")'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.PositiveIntegerField', ['_(u"Position")'], {'default': '999'})
        },
        'criteria.usercriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'users': ('models.ManyToManyField', ['User'], {})
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
        'criteria.countrycriterion': {
            'countries': ('models.ManyToManyField', ['Country'], {'verbose_name': '_(u"Countries")'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'})
        },
        'criteria.cartpricecriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'})
        },
        'criteria.widthcriterion': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'operator': ('models.PositiveIntegerField', ['_(u"Operator")'], {'null': 'True', 'blank': 'True'}),
            'width': ('models.FloatField', ['_(u"Width")'], {'default': '0.0'})
        }
    }
    
    complete_apps = ['criteria']
