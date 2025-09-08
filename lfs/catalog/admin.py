from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from lfs.catalog.models import Product, Category, StaticBlock


class CategoryAdmin(admin.ModelAdmin):
    """
    Beautiful hierarchical admin interface for Category model.
    """

    list_display = (
        "indented_name",
        "slug",
        "position",
        "level",
        "product_count",
        "children_count",
        "show_all_products",
        "exclude_from_navigation",
        "image_preview",
    )
    list_display_links = ("indented_name",)
    list_filter = (
        "level",
        "show_all_products",
        "exclude_from_navigation",
        "parent",
    )
    search_fields = ("name", "slug", "short_description")
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "parent", "position")}),
        ("Content", {"fields": ("short_description", "description", "image")}),
        ("Settings", {"fields": ("show_all_products", "exclude_from_navigation", "template", "static_block")}),
        (
            "Format Settings",
            {"fields": ("active_formats", "product_rows", "product_cols", "category_cols"), "classes": ("collapse",)},
        ),
        ("SEO", {"fields": ("meta_title", "meta_keywords", "meta_description"), "classes": ("collapse",)}),
        ("Advanced", {"fields": ("level", "uid"), "classes": ("collapse",)}),
    )

    readonly_fields = ("level", "uid")
    ordering = ("level", "position", "name")

    # Enable bulk actions
    actions = ["make_navigation_visible", "make_navigation_hidden", "reset_positions"]

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset(request).select_related("parent", "static_block").prefetch_related("products")

    def indented_name(self, obj):
        """Display category name with indentation based on hierarchy level."""
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * (obj.level - 1) if obj.level > 1 else ""
        icon = "📁" if obj.get_children().exists() else "📄"

        return format_html("{}{} <strong>{}</strong>", mark_safe(indent), icon, obj.name)

    indented_name.short_description = "Category Name"
    indented_name.admin_order_field = "name"

    def product_count(self, obj):
        """Display number of products in this category."""
        count = obj.products.count()
        if count > 0:
            url = reverse("admin:catalog_product_changelist") + f"?categories__id__exact={obj.id}"
            return format_html('<a href="{}">{} products</a>', url, count)
        return "0 products"

    product_count.short_description = "Products"

    def children_count(self, obj):
        """Display number of child categories."""
        count = obj.get_children().count()
        if count > 0:
            url = reverse("admin:catalog_category_changelist") + f"?parent__id__exact={obj.id}"
            return format_html('<a href="{}">{} children</a>', url, count)
        return "0 children"

    children_count.short_description = "Children"

    def image_preview(self, obj):
        """Display small preview of category image."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url_100x100,
            )
        return "🖼️ No image"

    image_preview.short_description = "Image"

    def make_navigation_visible(self, request, queryset):
        """Bulk action to make categories visible in navigation."""
        updated = queryset.update(exclude_from_navigation=False)
        self.message_user(request, f"{updated} categories are now visible in navigation.")

    make_navigation_visible.short_description = "Make visible in navigation"

    def make_navigation_hidden(self, request, queryset):
        """Bulk action to hide categories from navigation."""
        updated = queryset.update(exclude_from_navigation=True)
        self.message_user(request, f"{updated} categories are now hidden from navigation.")

    make_navigation_hidden.short_description = "Hide from navigation"

    def reset_positions(self, request, queryset):
        """Bulk action to reset positions to sequential order."""
        for i, category in enumerate(queryset.order_by("name"), start=1):
            category.position = i * 10
            category.save()
        self.message_user(request, f"Positions reset for {queryset.count()} categories.")

    reset_positions.short_description = "Reset positions"

    def save_model(self, request, obj, form, change):
        """Override save to automatically set level based on parent."""
        if obj.parent:
            obj.level = obj.parent.level + 1
        else:
            obj.level = 1
        super().save_model(request, obj, form, change)


# Register the models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
admin.site.register(StaticBlock)
