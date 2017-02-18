import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Regenerate thumbnails for Shop, Category and Image models if they are missing.'

    def handle(self, *args, **options):
        from django.conf import settings
        from lfs.core.models import Shop
        from lfs.core.fields import thumbs
        from lfs.catalog.settings import THUMBNAIL_SIZES
        from lfs.catalog.models import Category
        from lfs.catalog.models import Image

        for m in [Shop, Category, Image]:
            for o in m.objects.all():
                img_file = getattr(o, 'image')
                if img_file.name:
                    self.stdout.write("Converting %s" % img_file.name)
                    for size in THUMBNAIL_SIZES:
                        (w, h) = size
                        split = img_file.name.rsplit('.', 1)
                        thumb_name = '%s.%sx%s.%s' % (split[0], w, h, split[1])
                        if os.path.isfile("%s/%s" % (settings.MEDIA_ROOT, thumb_name)):
                            self.stdout.write("\tSize %sx%s already exists" % (w, h))
                            continue

                        thumb_content = thumbs.generate_thumb(img_file, size, split[1])
                        img_file.storage.save(thumb_name, thumb_content)
                        self.stdout.write("\tSize %sx%s created" % (w, h))
