# django importsad
from django.core.management.base import BaseCommand
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.voucher.models import Voucher
import lfs.core.settings as lfs_settings

# south imports
from south.db import db


class Command(BaseCommand):
    args = ''
    help = 'Migrations for LFS'

    def handle(self, *args, **options):
        """
        """
        # 0.5 -> trunk
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
            models.CharField(choices=lfs_settings.LFS_PRICE_CALCULATOR_DICTIONARY.items(), default=lfs_settings.LFS_DEFAULT_PRICE_CALCULATOR, max_length=255))

        # Locale and currency settings
        db.add_column("core_shop", "default_locale",
            models.CharField(_(u"Default Shop Locale"), max_length=20, default="de_DE.UTF-8"))
        db.add_column("core_shop", "use_international_currency_code",
            models.BooleanField(_(u"Use international currency codes"), default=False))
        db.delete_column('core_shop', 'default_currency')

        db.add_column("catalog_product", "supplier_id", models.IntegerField(blank=True, null=True))
