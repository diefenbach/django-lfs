# django imports
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView

# lfs imports
from .services import RatingMailService


class RatingMailManageView(PermissionRequiredMixin, TemplateView):
    """Displays the manage view for rating mails."""

    template_name = "manage/review_mails/rating_mails.html"
    permission_required = "core.manage_shop"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = RatingMailService(request=self.request)
        context["eligible_orders"] = service.get_orders_for_rating_mails()
        return context


class RatingMailSendView(PermissionRequiredMixin, SuccessMessageMixin, TemplateView):
    """Handles sending rating mails."""

    template_name = "manage/review_mails/rating_mails.html"
    permission_required = "core.manage_shop"
    success_message = _("Rating mails have been sent successfully.")

    def post(self, request, *args, **kwargs):
        """Handle POST request to send rating mails."""
        service = RatingMailService(request=request)

        # Get eligible orders
        eligible_orders = service.get_orders_for_rating_mails()

        # Determine if this is a test run
        is_test = request.POST.get("test") is not None
        include_bcc = request.POST.get("bcc") is not None

        # Send mails
        sent_orders = service.send_rating_mails_batch(eligible_orders, is_test=is_test, include_bcc=include_bcc)

        # Prepare context for response
        context = self.get_context_data(**kwargs)
        context["display_orders_sent"] = True
        context["orders_sent"] = sent_orders
        context["eligible_orders"] = eligible_orders

        if is_test:
            messages.info(request, _("Test mails sent to shop notification emails."))
        else:
            messages.success(request, _("Rating mails sent to {} customers.").format(len(sent_orders)))

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = RatingMailService(request=self.request)
        context["eligible_orders"] = service.get_orders_for_rating_mails()
        return context
