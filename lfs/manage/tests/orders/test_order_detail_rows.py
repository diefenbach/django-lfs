"""The order detail page of the management interface shows what LFS knows about an order, and nothing of one shop.

It used to show "Lieferzeit", "Gesamtgewicht" and "Europallettentausch möglich" (hard-coded in German) in every
shop; weight and pallet exchange come from the Höhne add-on hoehne-order-extensions, which fills the block
``order_extra_info`` itself.
"""

from django.urls import reverse

from lfs.order.models import OrderDeliveryTime


def test_order_detail_shows_no_rows_of_a_shop_specific_add_on(authenticated_client, order_with_items):
    response = authenticated_client.get(reverse("lfs_manage_order", kwargs={"order_id": order_with_items.id}))

    content = response.content.decode()
    assert response.status_code == 200
    for text in ("Europallettentausch", "Gesamtgewicht", "Lieferzeit"):
        assert text not in content


def test_order_detail_shows_the_delivery_time_of_the_order(authenticated_client, order_with_items):
    OrderDeliveryTime.objects.create(order=order_with_items, min=2, max=3, unit=2)

    response = authenticated_client.get(reverse("lfs_manage_order", kwargs={"order_id": order_with_items.id}))

    content = response.content.decode()
    assert "Delivery time" in content
    assert OrderDeliveryTime.objects.get().round().as_string() in content
