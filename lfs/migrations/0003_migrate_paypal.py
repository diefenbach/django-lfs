# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

from lfs.payment.models import PaymentMethod


class Migration(SchemaMigration):

    def forwards(self, orm):
        paypal = PaymentMethod.objects.get(pk=3)
        paypal.module = "lfs_paypal.PayPalProcessor"
        paypal.save()    
    def backwards(self, orm):
        raise NotImplementedError("Backward migration is not supported.")
