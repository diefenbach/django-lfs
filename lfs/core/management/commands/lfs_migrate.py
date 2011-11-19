# django importsad
from django.core.management.base import BaseCommand
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.settings as lfs_settings
from lfs.voucher.models import Voucher

# south imports
from south.db import db


class Command(BaseCommand):
    args = ''
    help = 'Migrations for LFS'

    def handle(self, *args, **options):
        """
        """
        from lfs.core.models import Application
        try:
            application = Application.objects.get(pk=1)
        except Application.DoesNotExist:
            application = Application.objects.create(version="0.5")

        version = application.version
        print "Detected version: %s" % version

        # 0.5 -> 0.6
        if version == "0.5":
            print "Migrating to 0.6"
            db.add_column("voucher_voucher", "used_amount", models.PositiveSmallIntegerField(default=0))
            db.add_column("voucher_voucher", "last_used_date", models.DateTimeField(blank=True, null=True))
            db.add_column("voucher_voucher", "limit", models.PositiveSmallIntegerField(default=1))

            for voucher in Voucher.objects.all():
                voucher.limit = 1
                voucher.save()

            # This mus be done with execute because the old fields are not there
            # anymore (and therefore can't be accessed via attribute) after the user
            # has upgraded to the latest version.
            db.execute("update voucher_voucher set used_amount = 1 where used = 1")
            db.execute("update voucher_voucher set used_amount = 0 where used = 0")
            db.execute("update voucher_voucher set last_used_date = used_date")

            db.delete_column('voucher_voucher', 'used')
            db.delete_column('voucher_voucher', 'used_date')

            # price calculator
            db.add_column("catalog_product", "price_calculator", models.CharField(
                null=True, blank=True, choices=lfs_settings.LFS_PRICE_CALCULATOR_DICTIONARY.items(), max_length=255))

            db.add_column("core_shop", "price_calculator",
                models.CharField(choices=lfs_settings.LFS_PRICE_CALCULATOR_DICTIONARY.items(), default="lfs.gross_price.GrossPriceCalculator", max_length=255))

            # Locale and currency settings
            db.add_column("core_shop", "default_locale",
                models.CharField(_(u"Default Shop Locale"), max_length=20, default="en_US.UTF-8"))
            db.add_column("core_shop", "use_international_currency_code",
                models.BooleanField(_(u"Use international currency codes"), default=False))
            db.delete_column('core_shop', 'default_currency')

            db.add_column("catalog_product", "supplier_id", models.IntegerField(_(u"Supplier"), blank=True, null=True))

            print "Your database has been migrated to version 0.6."

            application.version = "0.6"
            application.save()
        if version == "0.6":
            print "You are up-to-date"
