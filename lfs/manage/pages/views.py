from typing import Dict, List, Tuple, Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView, DeleteView, RedirectView, TemplateView

from lfs.caching.utils import lfs_get_object_or_404
from lfs.manage.mixins import DirectDeleteMixin
from lfs.manage.pages.forms import PageAddForm, PageForm
from lfs.manage.views.lfs_portlets import PortletsInlineView
from lfs.page.models import Page


class ManagePagesView(PermissionRequiredMixin, RedirectView):
    """Dispatches to the first page or to the add page form."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        try:
            page = Page.objects.all()[0]
            return reverse("lfs_manage_page", kwargs={"id": page.id})
        except IndexError:
            return reverse("lfs_add_page")


class PageTabMixin:
    """Mixin for tab navigation in Page views."""

    template_name = "manage/pages/page.html"
    tab_name: Optional[str] = None

    def get_page(self) -> Page:
        """Gets the Page object."""
        return get_object_or_404(Page, pk=self.kwargs["id"])

    def get_pages_queryset(self):
        """Returns filtered Pages based on search parameter."""
        queryset = Page.objects.exclude(pk=1).order_by("title")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with tab navigation and Page."""
        ctx = super().get_context_data(**kwargs)
        page = getattr(self, "object", None) or self.get_page()

        ctx.update(
            {
                "page": page,
                "active_tab": self.tab_name,
                "tabs": self._get_tabs(page),
                **self._get_navigation_context(page),
            }
        )
        return ctx

    def _get_tabs(self, page: Page) -> List[Tuple[str, str]]:
        """Creates tab navigation URLs with search parameter."""
        search_query = self.request.GET.get("q", "").strip()

        portlets_url = reverse("lfs_manage_page_portlets", args=[page.pk])

        # Add search parameter if present
        if search_query:
            from urllib.parse import urlencode

            query_params = urlencode({"q": search_query})
            portlets_url += "?" + query_params

        tabs = []

        # For root page (id=1), only show portlets tab
        if page.id == 1:
            tabs.append(("portlets", portlets_url))
        else:
            # For other pages, show data, seo, and portlets tabs
            data_url = reverse("lfs_manage_page", args=[page.pk])
            seo_url = reverse("lfs_manage_page_seo", args=[page.pk])

            if search_query:
                from urllib.parse import urlencode

                query_params = urlencode({"q": search_query})
                data_url += "?" + query_params
                seo_url += "?" + query_params

            tabs.extend(
                [
                    ("data", data_url),
                    ("seo", seo_url),
                    ("portlets", portlets_url),
                ]
            )

        return tabs

    def _get_navigation_context(self, page: Page) -> Dict[str, Any]:
        """Returns navigation context data."""
        return {
            "root": Page.objects.get(pk=1),
            "page": page,
            "pages": self.get_pages_queryset(),
            "search_query": self.request.GET.get("q", ""),
        }


class PageDataView(PermissionRequiredMixin, PageTabMixin, UpdateView):
    """View for data tab of a Page."""

    model = Page
    form_class = PageForm
    tab_name = "data"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Redirects root page to portlets tab."""
        if self.kwargs["id"] == "1":
            return HttpResponseRedirect(reverse("lfs_manage_page_portlets", kwargs={"id": "1"}))
        return super().get(request, *args, **kwargs)

    def get_success_url(self) -> str:
        """Stays on the data tab after successful save."""
        return reverse("lfs_manage_page", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        # Handle file deletion if checkbox is checked
        if self.request.POST.get("delete_file"):
            page = self.get_object()
            if page.file:
                page.file.delete()
                page.file = None
                page.save()

        response = super().form_valid(form)
        messages.success(self.request, _("Page has been saved."))
        return response


class PageSEOView(PermissionRequiredMixin, PageTabMixin, UpdateView):
    """View for SEO tab of a Page."""

    model = Page
    fields = ["meta_title", "meta_description", "meta_keywords"]
    tab_name = "seo"
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"

    def get_success_url(self) -> str:
        """Stays on the SEO tab after successful save."""
        return reverse("lfs_manage_page_seo", kwargs={"id": self.object.pk})

    def form_valid(self, form):
        """Saves and shows success message."""
        response = super().form_valid(form)
        messages.success(self.request, _("SEO data has been saved."))
        return response

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Prevents access to root page SEO."""
        if self.kwargs["id"] == "1":
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Prevents access to root page SEO."""
        if self.kwargs["id"] == "1":
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)


class PagePortletsView(PermissionRequiredMixin, PageTabMixin, TemplateView):
    """View for portlets tab of a Page."""

    tab_name = "portlets"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Extends context with portlets."""
        ctx = super().get_context_data(**kwargs)
        page = self.get_page()
        ctx["portlets"] = PortletsInlineView().get(self.request, page)
        return ctx


class PageCreateView(SuccessMessageMixin, PermissionRequiredMixin, CreateView):
    """Provides a form to add a new page."""

    model = Page
    form_class = PageAddForm
    template_name = "manage/pages/add_page.html"
    permission_required = "core.manage_shop"
    success_message = _("Page has been created.")

    def get_success_url(self):
        return reverse("lfs_manage_page", kwargs={"id": self.object.id})

    def form_valid(self, form):
        """Saves the page."""
        response = super().form_valid(form)
        return response


class PageDeleteConfirmView(PermissionRequiredMixin, TemplateView):
    """Provides a modal form to confirm deletion of a page."""

    template_name = "manage/pages/delete_page.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = get_object_or_404(Page, pk=self.kwargs["id"])
        return context


class PageDeleteView(DirectDeleteMixin, SuccessMessageMixin, PermissionRequiredMixin, DeleteView):
    """Deletes page with passed id."""

    model = Page
    pk_url_kwarg = "id"
    permission_required = "core.manage_shop"
    success_message = _("Page has been deleted.")

    def get_success_url(self):
        return reverse("lfs_manage_pages")


class PageViewByIDView(PermissionRequiredMixin, RedirectView):
    """Displays page with passed id."""

    permission_required = "core.manage_shop"

    def get_redirect_url(self, *args, **kwargs):
        page_id = self.kwargs["id"]
        if page_id == 1:
            raise Http404()

        page = lfs_get_object_or_404(Page, pk=page_id)
        return reverse("lfs_page_view", kwargs={"slug": page.slug})
