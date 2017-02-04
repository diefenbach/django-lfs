# django imports
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

# lfs imports
from lfs.manage.views.marketing.topseller import manage_topseller
from lfs.manage.views.marketing.featured import manage_featured


@permission_required("core.manage_shop")
def manage_marketing(request, template_name="manage/marketing/marketing.html"):
    """Displays the main manage/edit form for marketing.
    """
    topseller = manage_topseller(request)

    return render(request, template_name, {
        "topseller": topseller,
    })


@permission_required("manage_shop")
def manage_featured_page(request, template_name="manage/marketing/marketing_featured.html"):
    """Displays the main manage/edit form for featured products.
    """
    featured = manage_featured(request)

    return render(request, template_name, {
        "featured": featured,
    })
