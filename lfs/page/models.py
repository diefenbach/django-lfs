# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.managers import ActiveManager
from lfs.core.models import Shop


class Page(models.Model):
    """An simple HTML page, which may have an optional file to download.
    """
    active = models.BooleanField(_(u"Active"), default=False)
    title = models.CharField(_(u"Title"), max_length=100)
    slug = models.SlugField(_(u"Slug"), max_length=100)
    position = models.IntegerField(_(u"Position"), default=999)
    exclude_from_navigation = models.BooleanField(_(u"Exclude from navigation"), default=False)
    short_text = models.TextField(blank=True)
    body = models.TextField(_(u"Text"), blank=True)
    file = models.FileField(_(u"File"), blank=True, upload_to="files")

    objects = ActiveManager()

    class Meta:
        ordering = ("position", )

    def __unicode__(self):
        return self.title

    def get_image(self):
        """Returns the image for the page.
        """
        shop = lfs_get_object_or_404(Shop, pk=1)
        return shop.image

    def get_absolute_url(self):
        return ("lfs_page_view", (), {"slug": self.slug})
    get_absolute_url = models.permalink(get_absolute_url)
