# django imports
from django.core.management.base import BaseCommand

from lfs.utils import generator


class Command(BaseCommand):
    args = ''
    help = 'Generates mock products for LFS'

    def handle(self, *args, **options):
        generator.products(20)
