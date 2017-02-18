from optparse import make_option
import datetime
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = 'days'
    help = 'Clean carts older than 7 days'
    option_list = BaseCommand.option_list + (
        make_option('--days',
                    action='store',
                    dest='days',
                    default=7,
                    help='Remove carts modified before specified number of days'),
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
