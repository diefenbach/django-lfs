import datetime
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Clean carts older than 7 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            action='store',
            dest='days',
            default=7,
            help="Remove carts modified before specified number of days",
        )

    def handle(self, *args, **options):
        """
        """
        from lfs.cart.models import Cart
        days = int(options['days'])
        today = datetime.date.today()
        dt = today - datetime.timedelta(days=days)
        qs = Cart.objects.filter(modification_date__lt=dt)
        carts_count = qs.count()
        qs.delete()
        print "Removed %s carts" % carts_count
