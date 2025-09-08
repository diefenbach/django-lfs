from django.urls import path, re_path
import lfs.manage.categories.views

urlpatterns = [
    # Categories (refactored views)
    path(
        "",
        lfs.manage.categories.views.ManageCategoriesView.as_view(),
        name="lfs_manage_categories",
    ),
    path(
        "<int:id>/",
        lfs.manage.categories.views.CategoryDataView.as_view(),
        name="lfs_manage_category",
    ),
    path(
        "<int:id>/view/",
        lfs.manage.categories.views.CategoryViewView.as_view(),
        name="lfs_manage_category_view",
    ),
    path(
        "<int:id>/products/",
        lfs.manage.categories.views.CategoryProductsView.as_view(),
        name="lfs_manage_category_products",
    ),
    path(
        "<int:id>/seo/",
        lfs.manage.categories.views.CategorySEOView.as_view(),
        name="lfs_manage_category_seo",
    ),
    path(
        "<int:id>/portlets/",
        lfs.manage.categories.views.CategoryPortletsView.as_view(),
        name="lfs_manage_category_portlets",
    ),
    path(
        "<int:id>/view-by-id/",
        lfs.manage.categories.views.CategoryViewByIDView.as_view(),
        name="lfs_category_by_id",
    ),
    path(
        "add/",
        lfs.manage.categories.views.CategoryCreateView.as_view(),
        name="lfs_manage_add_top_category",
    ),
    path(
        "<int:parent_id>/add/",
        lfs.manage.categories.views.CategoryCreateView.as_view(),
        name="lfs_manage_add_category",
    ),
    path(
        "<int:id>/delete/",
        lfs.manage.categories.views.CategoryDeleteView.as_view(),
        name="lfs_delete_category",
    ),
    path(
        "<int:id>/delete/confirm/",
        lfs.manage.categories.views.CategoryDeleteConfirmView.as_view(),
        name="lfs_delete_category_confirm",
    ),
    path(
        "no-categories/",
        lfs.manage.categories.views.NoCategoriesView.as_view(),
        name="lfs_manage_no_categories",
    ),
    # Legacy category URLs for backward compatibility
    re_path(r"^sort-categories$", lfs.manage.categories.views.SortCategoriesView.as_view(), name="lfs_sort_categories"),
]
