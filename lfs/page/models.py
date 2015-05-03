# django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# lfs imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.managers import ActiveManager
from lfs.core.models import Shop
from lfs.core.utils import get_default_shop


class Page(models.Model):
    """An simple HTML page, which may have an optional file to download.
    """
    active = models.BooleanField(_(u"Active"), default=False)
    title = models.CharField(_(u"Title"), max_length=100)
    slug = models.SlugField(_(u"Slug"), unique=True, max_length=100)
    position = models.IntegerField(_(u"Position"), default=999)
    exclude_from_navigation = models.BooleanField(_(u"Exclude from navigation"), default=False)
    short_text = models.TextField(_(u"Short text"), blank=True)
    body = models.TextField(_(u"Text"), blank=True)
    file = models.FileField(_(u"File"), blank=True, upload_to="files")

    meta_title = models.CharField(_(u"Meta title"), blank=True, default="<title>", max_length=80)
    meta_keywords = models.TextField(_(u"Meta keywords"), blank=True)
    meta_description = models.TextField(_(u"Meta description"), blank=True)

    objects = ActiveManager()

    class Meta:
        ordering = ("position", )
        app_label = 'page'

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

    def get_parent_for_portlets(self):
        """Returns the parent for parents.
        """
        if self.id == 1:
            return get_default_shop()
        else:
            return lfs_get_object_or_404(Page, pk=1)

    def get_meta_title(self):
        """Returns the meta title of the page.
        """
        return self.meta_title.replace("<title>", self.title)

    def get_meta_keywords(self):
        """Returns the meta keywords of the page.
        """
        mk = self.meta_keywords.replace("<title>", self.title)
        return mk.replace("<short-text>", self.short_text)

    def get_meta_description(self):
        """Returns the meta description of the page.
        """
        md = self.meta_description.replace("<title>", self.title)
        return md.replace("<short-text>", self.short_text)
