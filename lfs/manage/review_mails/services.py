# django imports
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

# lfs imports
import lfs.core.utils
import lfs.marketing.utils
from lfs.catalog.models import Product
from lfs.marketing.models import OrderRatingMail


class RatingMailService:
    """Service for handling rating mail operations."""

    def __init__(self, request=None):
        self.request = request
        self.ctype = ContentType.objects.get_for_model(Product)
        self.site = "http://%s" % Site.objects.get(id=settings.SITE_ID)
        self.shop = lfs.core.utils.get_default_shop()

    def get_orders_for_rating_mails(self):
        """Get orders that are eligible for rating mails."""
        eligible_orders = []

        for order in lfs.marketing.utils.get_orders():
            try:
                OrderRatingMail.objects.get(order=order)
            except OrderRatingMail.DoesNotExist:
                eligible_orders.append(order)

        return eligible_orders

    def generate_email_content(self, order):
        """Generate email content for a given order."""
        # Get order items with product information
        order_items = []
        for order_item in order.items.all():
            product = order_item.product
            if not product:
                continue
            if product.is_variant():
                product = product.parent

            order_items.append(
                {
                    "product_id": product.id,
                    "product_name": product.name,
                }
            )

        # Generate text content
        text_content = render_to_string(
            "lfs/reviews/rating_mail.txt",
            request=self.request,
            context={
                "order": order,
                "content_type_id": self.ctype.id,
                "site": self.site,
            },
        )

        # Generate HTML content
        html_content = render_to_string(
            "lfs/reviews/rating_mail.html",
            request=self.request,
            context={
                "order": order,
                "order_items": order_items,
                "content_type_id": self.ctype.id,
                "site": self.site,
            },
        )

        return {
            "text": text_content,
            "html": html_content,
            "order_items": order_items,
        }

    def send_rating_mail(self, order, is_test=False, include_bcc=False):
        """Send rating mail for a given order."""
        # Generate email content
        content = self.generate_email_content(order)

        # Prepare email details
        subject = _("Please rate your products on ") + self.shop.name
        from_email = self.shop.from_email

        if is_test:
            to = self.shop.get_notification_emails()
            bcc = []
        else:
            to = [order.customer_email]
            if include_bcc:
                bcc = self.shop.get_notification_emails()
            else:
                bcc = []
            # Mark as sent
            OrderRatingMail.objects.create(order=order)

        # Create and send email
        mail = EmailMultiAlternatives(subject=subject, body=content["text"], from_email=from_email, to=to, bcc=bcc)
        mail.attach_alternative(content["html"], "text/html")
        mail.send()

        return True

    def send_rating_mails_batch(self, orders, is_test=False, include_bcc=False):
        """Send rating mails for multiple orders."""
        sent_orders = []

        for order in orders:
            try:
                self.send_rating_mail(order, is_test=is_test, include_bcc=include_bcc)
                sent_orders.append(order)
            except Exception as e:
                # Log error but continue with other orders
                # In a real implementation, you might want to log this properly
                continue

        return sent_orders
