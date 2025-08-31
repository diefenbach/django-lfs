"""
Tests for refactored cart management views.
"""

from django.urls import reverse

from lfs.cart.models import Cart


def test_manage_carts_view_redirects_to_first_cart(authenticated_client, test_carts):
    """Test that ManageCartsView redirects to the first cart."""
    response = authenticated_client.get(reverse("lfs_manage_carts"))
    # Should redirect to the first cart (most recent by modification_date)
    assert response.status_code == 302


def test_manage_carts_view_redirects_to_no_carts_when_empty(authenticated_client):
    """Test that ManageCartsView redirects to no carts view when no carts exist."""
    Cart.objects.all().delete()
    response = authenticated_client.get(reverse("lfs_manage_carts"))
    assert response.status_code == 302
    assert response.url == reverse("lfs_manage_no_carts")


def test_no_carts_view_renders_correctly(authenticated_client):
    """Test that NoCartsView renders the correct template."""
    Cart.objects.all().delete()
    response = authenticated_client.get(reverse("lfs_manage_no_carts"))
    assert response.status_code == 200
    assert "no carts" in response.content.decode().lower()


def test_cart_data_view_renders_correctly(authenticated_client, test_carts):
    """Test that CartDataView renders the cart data correctly."""
    cart1, cart2 = test_carts
    response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
    assert response.status_code == 200
    assert "cart" in response.content.decode().lower()


def test_apply_cart_filters_view_processes_form(authenticated_client, test_carts):
    """Test that ApplyCartFiltersView processes filter form correctly."""
    cart1, cart2 = test_carts
    response = authenticated_client.post(
        reverse("lfs_apply_cart_filters", kwargs={"id": cart1.id}),
        {"start": "2023-01-01", "end": "2023-12-31"},  # ISO format (testing settings)
    )
    assert response.status_code == 302  # Should redirect after processing

    # Check that filters are saved in localized format
    session = authenticated_client.session
    cart_filters = session.get("cart-filters", {})
    assert "start" in cart_filters
    assert "end" in cart_filters


def test_cart_delete_confirm_view_renders_correctly(authenticated_client, test_carts):
    """Test that CartDeleteConfirmView renders correctly."""
    cart1, cart2 = test_carts
    response = authenticated_client.get(reverse("lfs_manage_delete_cart_confirm", kwargs={"id": cart1.id}))
    assert response.status_code == 200


def test_cart_delete_view_deletes_cart(authenticated_client, test_carts):
    """Test that CartDeleteView actually deletes the cart."""
    cart1, cart2 = test_carts
    cart_id = cart1.id
    response = authenticated_client.post(reverse("lfs_delete_cart", kwargs={"id": cart_id}))

    # Should redirect after deletion
    assert response.status_code == 302

    # Cart should be deleted
    assert not Cart.objects.filter(id=cart_id).exists()


def test_reset_cart_filters_view_clears_session(authenticated_client):
    """Test that ResetCartFiltersView clears the cart filters from session."""
    # Set some filters in session
    session = authenticated_client.session
    session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
    session.save()

    response = authenticated_client.get(reverse("lfs_reset_cart_filters"))

    # Should redirect
    assert response.status_code == 302

    # Filters should be cleared
    assert "cart-filters" not in authenticated_client.session


def test_sidebar_pagination_shows_10_carts_per_page(authenticated_client, test_carts):
    """Test that sidebar shows 10 carts per page."""
    cart1, cart2 = test_carts
    # Create 15 carts to test pagination (plus the 2 existing = 17 total)
    for i in range(15):
        Cart.objects.create(session=f"test_session_{i}")

    response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
    assert response.status_code == 200

    # Should have pagination context
    assert "carts_page" in response.context
    carts_page = response.context["carts_page"]

    # Should show 10 carts per page
    assert len(carts_page) == 10
    assert carts_page.has_next()


def test_sidebar_filter_form_is_present(authenticated_client, test_carts):
    """Test that sidebar contains the filter form."""
    cart1, cart2 = test_carts
    response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
    assert response.status_code == 200

    # Should have filter form in context
    assert "filter_form" in response.context

    # Should contain filter form in HTML
    content = response.content.decode()
    assert 'name="start"' in content
    assert 'name="end"' in content

    # Should use Flatpickr class (check for the actual class that's being used)
    assert "dateinput" in content


def test_date_format_parsing(authenticated_client, test_carts):
    """Test that various date formats are parsed correctly (testing uses ISO)."""
    cart1, cart2 = test_carts

    # Test ISO format (primary in testing settings)
    session = authenticated_client.session
    session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
    session.save()

    response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
    assert response.status_code == 200

    # Test US format (compatibility)
    session["cart-filters"] = {"start": "12/31/2023", "end": "01/01/2024"}
    session.save()

    response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
    assert response.status_code == 200

    # Test German format (compatibility)
    session["cart-filters"] = {"start": "31.12.2023", "end": "01.01.2024"}
    session.save()

    response = authenticated_client.get(reverse("lfs_manage_cart", kwargs={"id": cart1.id}))
    assert response.status_code == 200


def test_reset_cart_filters_with_cart_id_parameter(authenticated_client, test_carts):
    """Test that reset cart filters works with cart_id parameter."""
    cart1, cart2 = test_carts

    # Set some filters first
    session = authenticated_client.session
    session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
    session.save()

    # Reset filters with cart_id parameter (should redirect back to cart)
    response = authenticated_client.get(reverse("lfs_reset_cart_filters") + f"?cart_id={cart1.id}")

    # Should redirect successfully
    assert response.status_code == 302

    # Should redirect to the cart view, not the old filters view
    assert response.url == reverse("lfs_manage_cart", kwargs={"id": cart1.id})

    # Filters should be cleared
    session = authenticated_client.session
    assert "cart-filters" not in session
