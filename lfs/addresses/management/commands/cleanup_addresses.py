import datetime

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = 'Remove unused addresses without customer or order'

    def handle(self, *args, **options):
        from lfs.addresses.models import BaseAddress
        cnt = 0
        ten_days_ago = datetime.date.today() - datetime.timedelta(days=10)
        for address in BaseAddress.objects.filter(order__isnull=True, customer__isnull=True, created__lt=ten_days_ago):
            address.delete()
            cnt += 1
        print "Removed %s addresses" % cnt
