from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from lfs.page.models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "position", "active", "exclude_from_navigation", "has_file", "view_on_site"]
    list_filter = ["active", "exclude_from_navigation", "position"]
    search_fields = ["title", "slug", "short_text", "body"]
    list_editable = ["active", "position", "exclude_from_navigation"]
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (_("Basic Information"), {"fields": ("title", "slug", "active", "position", "exclude_from_navigation")}),
        (_("Content"), {"fields": ("short_text", "body", "file")}),
        (_("SEO"), {"fields": ("meta_title", "meta_keywords", "meta_description"), "classes": ("collapse",)}),
    )

    def has_file(self, obj):
        """Display if page has a file attached."""
        return bool(obj.file)

    has_file.boolean = True
    has_file.short_description = _("Has File")

    def view_on_site(self, obj):
        """Provide a link to view the page on the site."""
        if obj.pk:
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">{}</a>', url, _("View"))
        return "-"

    view_on_site.short_description = _("View on Site")

    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        return super().get_queryset(request).select_related()

    class Media:
        css = {"all": ("admin/css/page_admin.css",)}
        js = ("admin/js/page_admin.js",)
