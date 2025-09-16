"""
Unit tests for Tools utility functions.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Mock external dependencies
"""

import pytest
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.test import RequestFactory
from unittest.mock import MagicMock

from lfs.manage.tools.views import (
    clear_cache,
    set_category_levels,
    update_effective_price,
    reindex_topseller,
)

User = get_user_model()


@pytest.fixture
def request_with_messages(admin_user):
    """Request with messages middleware support."""
    factory = RequestFactory()
    request = factory.get("/")
    request.user = admin_user
    request.session = {}

    # Mock the messages framework properly
    from django.contrib.messages.storage.fallback import FallbackStorage

    request._messages = FallbackStorage(request)

    return request


class TestClearCache:
    """Test the clear_cache utility function."""

    def test_clear_cache_calls_caching_utils(self, request_with_messages, monkeypatch):
        """Should call lfs.caching.utils.clear_cache()."""
        clear_cache_mock = MagicMock()
        monkeypatch.setattr("lfs.manage.tools.views.lfs.caching.utils.clear_cache", clear_cache_mock)

        clear_cache(request_with_messages)

        clear_cache_mock.assert_called_once()

    def test_clear_cache_adds_success_message(self, request_with_messages, monkeypatch):
        """Should add success message to request."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.caching.utils.clear_cache", MagicMock())

        clear_cache(request_with_messages)

        # Check that messages were added
        message_list = list(messages.get_messages(request_with_messages))
        assert len(message_list) == 1
        assert "Cache has been cleared" in str(message_list[0])

    def test_clear_cache_redirects_to_tools(self, request_with_messages, monkeypatch):
        """Should redirect to tools view."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.caching.utils.clear_cache", MagicMock())

        response = clear_cache(request_with_messages)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_tools")

    def test_clear_cache_works_with_regular_user(self, regular_user, monkeypatch):
        """Should work with regular user (permission check is at decorator level)."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.caching.utils.clear_cache", MagicMock())

        factory = RequestFactory()
        request = factory.get("/")
        request.user = regular_user
        request.session = {}

        # Mock the messages framework
        from django.contrib.messages.storage.fallback import FallbackStorage

        request._messages = FallbackStorage(request)

        # The function should still work but the permission check happens at the decorator level
        response = clear_cache(request)
        assert isinstance(response, HttpResponseRedirect)


class TestSetCategoryLevels:
    """Test the set_category_levels utility function."""

    def test_set_category_levels_calls_core_utils(self, request_with_messages, monkeypatch):
        """Should call lfs.core.utils.set_category_levels()."""
        set_category_levels_mock = MagicMock()
        monkeypatch.setattr("lfs.manage.tools.views.lfs.core.utils.set_category_levels", set_category_levels_mock)

        set_category_levels(request_with_messages)

        set_category_levels_mock.assert_called_once()

    def test_set_category_levels_adds_success_message(self, request_with_messages, monkeypatch):
        """Should add success message to request."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.core.utils.set_category_levels", MagicMock())

        set_category_levels(request_with_messages)

        # Check that messages were added
        message_list = list(messages.get_messages(request_with_messages))
        assert len(message_list) == 1
        assert "Category levels have been created" in str(message_list[0])

    def test_set_category_levels_redirects_to_tools(self, request_with_messages, monkeypatch):
        """Should redirect to tools view."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.core.utils.set_category_levels", MagicMock())

        response = set_category_levels(request_with_messages)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_tools")

    def test_set_category_levels_works_with_regular_user(self, regular_user, monkeypatch):
        """Should work with regular user (permission check is at decorator level)."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.core.utils.set_category_levels", MagicMock())

        factory = RequestFactory()
        request = factory.get("/")
        request.user = regular_user
        request.session = {}

        # Mock the messages framework
        from django.contrib.messages.storage.fallback import FallbackStorage

        request._messages = FallbackStorage(request)

        response = set_category_levels(request)
        assert isinstance(response, HttpResponseRedirect)


class TestUpdateEffectivePrice:
    """Test the update_effective_price utility function."""

    def test_update_effective_price_calls_save_on_all_products(
        self, request_with_messages, sample_products, monkeypatch
    ):
        """Should call save() on all products."""
        # Mock the Product.objects.all() to return our sample products
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = lambda self: iter(sample_products)
        monkeypatch.setattr("lfs.manage.tools.views.lfs.catalog.models.Product.objects.all", lambda: mock_queryset)

        # Track save calls
        save_calls = []
        for i, product in enumerate(sample_products):
            # Use a closure to capture the current product
            def make_save_func(p):
                return lambda: save_calls.append(p)

            product.save = make_save_func(product)

        update_effective_price(request_with_messages)

        assert len(save_calls) == len(sample_products)
        for product in sample_products:
            assert product in save_calls

    def test_update_effective_price_adds_success_message(self, request_with_messages, monkeypatch):
        """Should add success message to request."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = lambda self: iter([])
        monkeypatch.setattr("lfs.manage.tools.views.lfs.catalog.models.Product.objects.all", lambda: mock_queryset)

        update_effective_price(request_with_messages)

        # Check that messages were added
        message_list = list(messages.get_messages(request_with_messages))
        assert len(message_list) == 1
        assert "Effective prices have been set" in str(message_list[0])

    def test_update_effective_price_redirects_to_tools(self, request_with_messages, monkeypatch):
        """Should redirect to tools view."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = lambda self: iter([])
        monkeypatch.setattr("lfs.manage.tools.views.lfs.catalog.models.Product.objects.all", lambda: mock_queryset)

        response = update_effective_price(request_with_messages)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_tools")

    def test_update_effective_price_works_with_regular_user(self, regular_user, monkeypatch):
        """Should work with regular user (permission check is at decorator level)."""
        mock_queryset = MagicMock()
        mock_queryset.__iter__ = lambda self: iter([])
        monkeypatch.setattr("lfs.manage.tools.views.lfs.catalog.models.Product.objects.all", lambda: mock_queryset)

        factory = RequestFactory()
        request = factory.get("/")
        request.user = regular_user
        request.session = {}

        # Mock the messages framework
        from django.contrib.messages.storage.fallback import FallbackStorage

        request._messages = FallbackStorage(request)

        response = update_effective_price(request)
        assert isinstance(response, HttpResponseRedirect)


class TestReindexTopseller:
    """Test the reindex_topseller utility function."""

    def test_reindex_topseller_calls_marketing_utils(self, request_with_messages, monkeypatch):
        """Should call lfs.marketing.utils.calculate_product_sales()."""
        calculate_sales_mock = MagicMock()
        monkeypatch.setattr("lfs.manage.tools.views.lfs.marketing.utils.calculate_product_sales", calculate_sales_mock)

        reindex_topseller(request_with_messages)

        calculate_sales_mock.assert_called_once()

    def test_reindex_topseller_adds_success_message(self, request_with_messages, monkeypatch):
        """Should add success message to request."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.marketing.utils.calculate_product_sales", MagicMock())

        reindex_topseller(request_with_messages)

        # Check that messages were added
        message_list = list(messages.get_messages(request_with_messages))
        assert len(message_list) == 1
        assert "Topseller have been reindexed" in str(message_list[0])

    def test_reindex_topseller_redirects_to_tools(self, request_with_messages, monkeypatch):
        """Should redirect to tools view."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.marketing.utils.calculate_product_sales", MagicMock())

        response = reindex_topseller(request_with_messages)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse("lfs_manage_tools")

    def test_reindex_topseller_works_with_regular_user(self, regular_user, monkeypatch):
        """Should work with regular user (permission check is at decorator level)."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.marketing.utils.calculate_product_sales", MagicMock())

        factory = RequestFactory()
        request = factory.get("/")
        request.user = regular_user
        request.session = {}

        # Mock the messages framework
        from django.contrib.messages.storage.fallback import FallbackStorage

        request._messages = FallbackStorage(request)

        response = reindex_topseller(request)
        assert isinstance(response, HttpResponseRedirect)


class TestUtilityFunctionsIntegration:
    """Integration tests for utility functions."""

    def test_all_utility_functions_redirect_to_same_url(self, request_with_messages, monkeypatch):
        """All utility functions should redirect to the same tools URL."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.caching.utils.clear_cache", MagicMock())
        monkeypatch.setattr("lfs.manage.tools.views.lfs.core.utils.set_category_levels", MagicMock())
        monkeypatch.setattr("lfs.manage.tools.views.lfs.marketing.utils.calculate_product_sales", MagicMock())

        mock_queryset = MagicMock()
        mock_queryset.__iter__ = lambda self: iter([])
        monkeypatch.setattr("lfs.manage.tools.views.lfs.catalog.models.Product.objects.all", lambda: mock_queryset)

        tools_url = reverse("lfs_manage_tools")

        clear_cache_response = clear_cache(request_with_messages)
        set_category_levels_response = set_category_levels(request_with_messages)
        update_effective_price_response = update_effective_price(request_with_messages)
        reindex_topseller_response = reindex_topseller(request_with_messages)

        assert clear_cache_response.url == tools_url
        assert set_category_levels_response.url == tools_url
        assert update_effective_price_response.url == tools_url
        assert reindex_topseller_response.url == tools_url

    def test_all_utility_functions_add_success_messages(self, request_with_messages, monkeypatch):
        """All utility functions should add success messages."""
        monkeypatch.setattr("lfs.manage.tools.views.lfs.caching.utils.clear_cache", MagicMock())
        monkeypatch.setattr("lfs.manage.tools.views.lfs.core.utils.set_category_levels", MagicMock())
        monkeypatch.setattr("lfs.manage.tools.views.lfs.marketing.utils.calculate_product_sales", MagicMock())

        mock_queryset = MagicMock()
        mock_queryset.__iter__ = lambda self: iter([])
        monkeypatch.setattr("lfs.manage.tools.views.lfs.catalog.models.Product.objects.all", lambda: mock_queryset)

        # Clear any existing messages
        list(messages.get_messages(request_with_messages))

        clear_cache(request_with_messages)
        set_category_levels(request_with_messages)
        update_effective_price(request_with_messages)
        reindex_topseller(request_with_messages)

        # Check that 4 success messages were added
        message_list = list(messages.get_messages(request_with_messages))
        assert len(message_list) == 4
