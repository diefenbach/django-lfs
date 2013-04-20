# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VoucherOptions'
        db.create_table('voucher_voucheroptions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number_prefix', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('number_suffix', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('number_length', self.gf('django.db.models.fields.IntegerField')(default=5, null=True, blank=True)),
            ('number_letters', self.gf('django.db.models.fields.CharField')(default='ABCDEFGHIJKLMNOPQRSTUVWXYZ', max_length=100, blank=True)),
        ))
        db.send_create_signal('voucher', ['VoucherOptions'])

        # Adding model 'VoucherGroup'
        db.create_table('voucher_vouchergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('position', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=10)),
        ))
        db.send_create_signal('voucher', ['VoucherGroup'])

        # Adding model 'Voucher'
        db.create_table('voucher_voucher', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='vouchers', to=orm['voucher.VoucherGroup'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('effective_from', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('kind_of', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('tax', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tax.Tax'], null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('used_amount', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('last_used_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('limit', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1, null=True, blank=True)),
        ))
        db.send_create_signal('voucher', ['Voucher'])


    def backwards(self, orm):
        # Deleting model 'VoucherOptions'
        db.delete_table('voucher_voucheroptions')

        # Deleting model 'VoucherGroup'
        db.delete_table('voucher_vouchergroup')

        # Deleting model 'Voucher'
        db.delete_table('voucher_voucher')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tax.tax': {
            'Meta': {'object_name': 'Tax'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'voucher.voucher': {
            'Meta': {'ordering': "('creation_date', 'number')", 'object_name': 'Voucher'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'effective_from': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vouchers'", 'to': "orm['voucher.VoucherGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind_of': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'last_used_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'tax': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tax.Tax']", 'null': 'True', 'blank': 'True'}),
            'used_amount': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'voucher.vouchergroup': {
            'Meta': {'ordering': "('position',)", 'object_name': 'VoucherGroup'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '10'})
        },
        'voucher.voucheroptions': {
            'Meta': {'object_name': 'VoucherOptions'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_length': ('django.db.models.fields.IntegerField', [], {'default': '5', 'null': 'True', 'blank': 'True'}),
            'number_letters': ('django.db.models.fields.CharField', [], {'default': "'ABCDEFGHIJKLMNOPQRSTUVWXYZ'", 'max_length': '100', 'blank': 'True'}),
            'number_prefix': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'number_suffix': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'})
        }
    }

    complete_apps = ['voucher']