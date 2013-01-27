from optparse import make_option
import datetime
from django.core.management.base import BaseCommand
from lfs.cart.models import Cart


class Command(BaseCommand):
    args = 'days'
    help = 'Clean carts older than 7 days'
    option_list = BaseCommand.option_list + (
            make_option('--days',
                action='store',
                dest='days',
                default=7,
                help='Remove carts modified before spefified number of days'),
            )

    def handle(self, *args, **options):
        """
        """
        days = int(options['days'])
        today = datetime.date.today()
        dt = today - datetime.timedelta(days=days)
        qs = Cart.objects.filter(modification_date__lt=dt)
        carts_count = qs.count()
        qs.delete()
        print "Removed %s carts" % carts_count

