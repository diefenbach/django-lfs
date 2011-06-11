# django imports
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.utils
import lfs.marketing.utils
from lfs.catalog.models import Product
from lfs.marketing.models import OrderRatingMail


@permission_required("core.manage_shop", login_url="/login/")
def manage_rating_mails(request, orders_sent=[], template_name="manage/marketing/rating_mails.html"):
    """Displays the manage view for rating mails
    """
    return render_to_response(template_name, RequestContext(request, {}))


@permission_required("core.manage_shop", login_url="/login/")
def send_rating_mails(request):
    """Send rating mails for given orders.
    """
    if request.method == "POST":
        ctype = ContentType.objects.get_for_model(Product)
        site = "http://%s" % Site.objects.get(id=settings.SITE_ID)

        shop = lfs.core.utils.get_default_shop()
        subject = _(u"Please rate your products on ")
        subject += shop.name
        from_email = shop.from_email

        orders_sent = []

        for order in lfs.marketing.utils.get_orders():

            try:
                OrderRatingMail.objects.get(order=order)
            except OrderRatingMail.DoesNotExist:
                pass
            else:
                continue

            orders_sent.append(order)

            if request.POST.get("test"):
                to = shop.get_notification_emails()
                bcc = []
            else:
                to = [order.customer_email]
                if request.POST.get("bcc"):
                    bcc = shop.get_notification_emails()
                else:
                    bcc = []
                OrderRatingMail.objects.create(order=order)

            # text
            text = render_to_string("lfs/reviews/rating_mail.txt", {
                "order": order,
                "content_type_id": ctype.id,
                "site": site,
            })

            mail = EmailMultiAlternatives(
                subject=subject, body=text, from_email=from_email, to=to, bcc=bcc)

            order_items = []
            for order_item in order.items.all():
                product = order_item.product
                if product.is_variant():
                    product = product.parent

                order_items.append({
                    "product_id": product.id,
                    "product_name": product.name,
                })

            # html
            html = render_to_string("lfs/reviews/rating_mail.html", {
                "order": order,
                "order_items": order_items,
                "content_type_id": ctype.id,
                "site": site,
            })

            mail.attach_alternative(html, "text/html")
            mail.send()

        return render_to_response("manage/marketing/rating_mails.html", RequestContext(request, {
            "display_orders_sent": True,
            "orders_sent": orders_sent
        }))
