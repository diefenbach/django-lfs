"""
Tests for refactored cart management views.
"""

from django.urls import reverse

from lfs.cart.models import Cart


def test_manage_carts_view_shows_cart_list(authenticated_client, test_carts):
    """Test that ManageCartsView shows the cart list template."""
    response = authenticated_client.get(reverse("lfs_manage_carts"))
    # Should show cart list template, not redirect
    assert response.status_code == 200
    assert "carts_with_data" in response.context


def test_manage_carts_view_shows_empty_list_when_no_carts(authenticated_client):
    """Test that ManageCartsView shows empty list when no carts exist."""
    Cart.objects.all().delete()
    response = authenticated_client.get(reverse("lfs_manage_carts"))
    assert response.status_code == 200
    assert len(response.context["carts_with_data"]) == 0


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


def test_cart_list_view_shows_15_carts_per_page(authenticated_client, test_carts):
    """Test that cart list shows 15 carts per page."""
    cart1, cart2 = test_carts
    # Create 20 carts to test pagination (plus the 2 existing = 22 total)
    for i in range(20):
        Cart.objects.create(session=f"test_session_{i}")

    response = authenticated_client.get(reverse("lfs_manage_carts"))
    assert response.status_code == 200

    # Should have pagination context
    assert "carts_page" in response.context
    carts_page = response.context["carts_page"]

    # Should show 15 carts per page in list view
    assert len(carts_page) == 15
    assert carts_page.has_next()


def test_cart_list_view_contains_cart_data(authenticated_client, test_carts):
    """Test that cart list view contains enriched cart data."""
    response = authenticated_client.get(reverse("lfs_manage_carts"))
    assert response.status_code == 200

    # Should have carts_with_data in context
    assert "carts_with_data" in response.context
    carts_with_data = response.context["carts_with_data"]

    # Should have at least the test carts
    assert len(carts_with_data) >= 2

    # Each cart data should have required fields
    for cart_data in carts_with_data:
        assert "cart" in cart_data
        assert "total" in cart_data
        assert "item_count" in cart_data
        assert "products" in cart_data
        assert "customer" in cart_data


def test_cart_list_filter_form_is_present(authenticated_client, test_carts):
    """Test that cart list contains the filter form."""
    response = authenticated_client.get(reverse("lfs_manage_carts"))
    assert response.status_code == 200

    # Should have filter form in context
    assert "filter_form" in response.context

    # Should contain filter form in HTML
    content = response.content.decode()
    assert 'name="start"' in content
    assert 'name="end"' in content
    assert "dateinput" in content


def test_apply_cart_filters_list_view_processes_form(authenticated_client, test_carts):
    """Test that ApplyCartFiltersView processes filter form correctly for list view."""
    response = authenticated_client.post(
        reverse("lfs_apply_cart_filters_list"),
        {"start": "2023-01-01", "end": "2023-12-31"},  # ISO format (testing settings)
    )
    assert response.status_code == 302  # Should redirect after processing
    assert response.url == reverse("lfs_manage_carts")  # Should redirect to list view

    # Check that filters are saved in session
    session = authenticated_client.session
    cart_filters = session.get("cart-filters", {})
    assert "start" in cart_filters
    assert "end" in cart_filters


def test_apply_predefined_cart_filter_list_view(authenticated_client, test_carts):
    """Test that predefined filters work for list view."""
    response = authenticated_client.get(
        reverse("lfs_apply_predefined_cart_filter_list", kwargs={"filter_type": "today"})
    )
    assert response.status_code == 302  # Should redirect after processing
    assert response.url == reverse("lfs_manage_carts")  # Should redirect to list view

    # Check that filters are saved in session
    session = authenticated_client.session
    cart_filters = session.get("cart-filters", {})
    assert "start" in cart_filters
    assert "end" in cart_filters


def test_cart_list_view_filtering_works(authenticated_client, test_carts):
    """Test that filtering works in cart list view."""
    # Set filters in session
    session = authenticated_client.session
    session["cart-filters"] = {"start": "2023-01-01", "end": "2023-12-31"}
    session.save()

    response = authenticated_client.get(reverse("lfs_manage_carts"))
    assert response.status_code == 200

    # Should apply filters to queryset
    assert "carts_page" in response.context
    # The actual filtering logic is tested in the view method tests


def test_cart_list_view_template_renders_correctly(authenticated_client, test_carts):
    """Test that cart list template renders correctly."""
    response = authenticated_client.get(reverse("lfs_manage_carts"))
    assert response.status_code == 200

    content = response.content.decode()
    # Should contain table headers
    assert "Cart ID" in content or "cart id" in content.lower()
    assert "Customer" in content or "customer" in content.lower()
    assert "Items" in content or "items" in content.lower()
    assert "Total" in content or "total" in content.lower()

    # Should contain filter toggle button
    assert "Filter" in content or "filter" in content.lower()

    # Should contain cart rows (clickable)
    assert "cart-row" in content
