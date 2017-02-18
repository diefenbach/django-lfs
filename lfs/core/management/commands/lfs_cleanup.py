from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = 'Call all lfs cleanup commands at once'

    def handle(self, *args, **options):
        management.call_command('cleanup_carts')
        management.call_command('cleanup_customers')
        management.call_command('cleanup_addresses')
