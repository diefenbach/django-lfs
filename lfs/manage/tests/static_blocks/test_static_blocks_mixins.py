"""
Comprehensive unit tests for static_blocks mixins.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking

Tests cover:
- StaticBlockTabMixin functionality
- Tab navigation and context data
- Search functionality
- URL generation
- Edge cases and error conditions
"""

import pytest
from django.http import Http404
from django.test import RequestFactory

from lfs.catalog.models import StaticBlock
from lfs.manage.static_blocks.views import StaticBlockTabMixin


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def mock_request(request_factory):
    """Mock request object for testing."""
    request = request_factory.get("/")
    request.session = {}
    return request


class TestStaticBlockTabMixin:
    """Test StaticBlockTabMixin functionality."""

    @pytest.mark.django_db
    def test_template_name_is_correct(self, mock_request):
        """Test that mixin has correct template name."""
        mixin = StaticBlockTabMixin()
        assert mixin.template_name == "manage/static_block/static_block.html"

    @pytest.mark.django_db
    def test_tab_name_is_none_by_default(self, mock_request):
        """Test that tab_name is None by default."""
        mixin = StaticBlockTabMixin()
        assert mixin.tab_name is None

    @pytest.mark.django_db
    def test_get_static_block_returns_correct_object(self, mock_request, sample_static_block):
        """Test that get_static_block returns the correct StaticBlock."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        result = mixin.get_static_block()

        assert result == sample_static_block

    @pytest.mark.django_db
    def test_get_static_block_raises_404_for_invalid_id(self, mock_request):
        """Test that get_static_block raises 404 for invalid ID."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": 99999}

        with pytest.raises(Http404):
            mixin.get_static_block()

    @pytest.mark.django_db
    def test_get_static_block_raises_404_for_nonexistent_id(self, mock_request):
        """Test that get_static_block raises 404 for nonexistent ID."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": 0}

        with pytest.raises(Http404):
            mixin.get_static_block()

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_returns_all_blocks(self, mock_request, sample_static_blocks):
        """Test that get_static_blocks_queryset returns all static blocks."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == len(sample_static_blocks)
        assert list(queryset) == list(StaticBlock.objects.all().order_by("name"))

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_orders_by_name(self, mock_request, sample_static_blocks):
        """Test that get_static_blocks_queryset orders by name."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        names = [block.name for block in queryset]
        assert names == sorted(names)

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_filters_by_search_query(self, mock_request, sample_static_blocks):
        """Test that get_static_blocks_queryset filters by search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "Block 1"}
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == 1
        assert queryset.first().name == "Test Static Block 1"

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_filters_by_partial_search_query(self, mock_request, sample_static_blocks):
        """Test that get_static_blocks_queryset filters by partial search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "Test"}
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == len(sample_static_blocks)
        for block in queryset:
            assert "Test" in block.name

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_handles_empty_search_query(self, mock_request, sample_static_blocks):
        """Test that get_static_blocks_queryset handles empty search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": ""}
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == len(sample_static_blocks)

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_handles_whitespace_search_query(self, mock_request, sample_static_blocks):
        """Test that get_static_blocks_queryset handles whitespace search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "   "}
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == len(sample_static_blocks)

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_handles_nonexistent_search_query(self, mock_request, sample_static_blocks):
        """Test that get_static_blocks_queryset handles nonexistent search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "Nonexistent"}
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == 0

    @pytest.mark.django_db
    def test_get_static_blocks_queryset_handles_no_search_parameter(self, mock_request, sample_static_blocks):
        """Test that get_static_blocks_queryset handles no search parameter."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {}
        mixin.request = mock_request

        queryset = mixin.get_static_blocks_queryset()

        assert queryset.count() == len(sample_static_blocks)

    @pytest.mark.django_db
    def test_get_context_data_includes_required_keys(self, mock_request, sample_static_block):
        """Test that get_context_data includes all required context keys."""
        from django.views.generic import TemplateView

        class TestView(StaticBlockTabMixin, TemplateView):
            pass

        view = TestView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}
        view.tab_name = "data"

        context = view.get_context_data()

        assert "static_block" in context
        assert "static_blocks" in context
        assert "search_query" in context
        assert "active_tab" in context
        assert "tabs" in context

    @pytest.mark.django_db
    def test_get_context_data_uses_object_if_available(self, mock_request, sample_static_block):
        """Test that get_context_data uses object if available."""
        from django.views.generic import TemplateView

        class TestView(StaticBlockTabMixin, TemplateView):
            pass

        view = TestView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}
        view.object = sample_static_block

        context = view.get_context_data()

        assert context["static_block"] == sample_static_block

    @pytest.mark.django_db
    def test_get_context_data_uses_get_static_block_if_no_object(self, mock_request, sample_static_block):
        """Test that get_context_data uses get_static_block if no object."""
        from django.views.generic import TemplateView

        class TestView(StaticBlockTabMixin, TemplateView):
            pass

        view = TestView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        context = view.get_context_data()

        assert context["static_block"] == sample_static_block

    @pytest.mark.django_db
    def test_get_context_data_includes_static_blocks_queryset(
        self, mock_request, sample_static_block, sample_static_blocks
    ):
        """Test that get_context_data includes static_blocks queryset."""
        from django.views.generic import TemplateView

        class TestView(StaticBlockTabMixin, TemplateView):
            pass

        view = TestView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        context = view.get_context_data()

        assert "static_blocks" in context
        # The queryset includes all static blocks, not just the sample ones
        assert context["static_blocks"].count() >= len(sample_static_blocks)

    @pytest.mark.django_db
    def test_get_context_data_includes_search_query(self, mock_request, sample_static_block):
        """Test that get_context_data includes search query."""
        from django.views.generic import TemplateView

        class TestView(StaticBlockTabMixin, TemplateView):
            pass

        view = TestView()
        mock_request.GET = {"q": "test search"}
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        context = view.get_context_data()

        assert context["search_query"] == "test search"

    @pytest.mark.django_db
    def test_get_context_data_includes_active_tab(self, mock_request, sample_static_block):
        """Test that get_context_data includes active tab."""
        from django.views.generic import TemplateView

        class TestView(StaticBlockTabMixin, TemplateView):
            pass

        view = TestView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}
        view.tab_name = "files"

        context = view.get_context_data()

        assert context["active_tab"] == "files"

    @pytest.mark.django_db
    def test_get_context_data_includes_tabs(self, mock_request, sample_static_block):
        """Test that get_context_data includes tabs."""
        from django.views.generic import TemplateView

        class TestView(StaticBlockTabMixin, TemplateView):
            pass

        view = TestView()
        view.request = mock_request
        view.kwargs = {"id": sample_static_block.id}

        context = view.get_context_data()

        assert "tabs" in context
        assert isinstance(context["tabs"], list)
        assert len(context["tabs"]) == 2

    @pytest.mark.django_db
    def test_get_tabs_returns_correct_tab_urls(self, mock_request, sample_static_block):
        """Test that _get_tabs returns correct tab URLs."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert len(tabs) == 2
        assert tabs[0][0] == "data"
        assert tabs[1][0] == "files"
        assert "/manage/static-block/" in tabs[0][1]
        assert "/manage/static-block/" in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_includes_search_query_in_urls(self, mock_request, sample_static_block):
        """Test that _get_tabs includes search query in URLs."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "test search"}
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "q=test+search" in tabs[0][1]
        assert "q=test+search" in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_handles_empty_search_query(self, mock_request, sample_static_block):
        """Test that _get_tabs handles empty search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": ""}
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "q=" not in tabs[0][1]
        assert "q=" not in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_handles_whitespace_search_query(self, mock_request, sample_static_block):
        """Test that _get_tabs handles whitespace search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "   "}
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "q=" not in tabs[0][1]
        assert "q=" not in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_handles_no_search_parameter(self, mock_request, sample_static_block):
        """Test that _get_tabs handles no search parameter."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {}
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "q=" not in tabs[0][1]
        assert "q=" not in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_uses_correct_static_block_id(self, mock_request, sample_static_block):
        """Test that _get_tabs uses correct static block ID."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert str(sample_static_block.pk) in tabs[0][1]
        assert str(sample_static_block.pk) in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_returns_tuples(self, mock_request, sample_static_block):
        """Test that _get_tabs returns tuples."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        for tab in tabs:
            assert isinstance(tab, tuple)
            assert len(tab) == 2

    @pytest.mark.django_db
    def test_get_tabs_first_tab_is_data(self, mock_request, sample_static_block):
        """Test that first tab is data."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert tabs[0][0] == "data"

    @pytest.mark.django_db
    def test_get_tabs_second_tab_is_files(self, mock_request, sample_static_block):
        """Test that second tab is files."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert tabs[1][0] == "files"

    @pytest.mark.django_db
    def test_get_tabs_data_url_contains_correct_view_name(self, mock_request, sample_static_block):
        """Test that data URL contains correct view name."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "/manage/static-block/" in tabs[0][1]

    @pytest.mark.django_db
    def test_get_tabs_files_url_contains_correct_view_name(self, mock_request, sample_static_block):
        """Test that files URL contains correct view name."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "/manage/static-block/" in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_urls_are_absolute(self, mock_request, sample_static_block):
        """Test that tab URLs are absolute."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        for tab in tabs:
            assert tab[1].startswith("/")

    @pytest.mark.django_db
    def test_get_tabs_urls_contain_static_block_id(self, mock_request, sample_static_block):
        """Test that tab URLs contain static block ID."""
        mixin = StaticBlockTabMixin()
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        for tab in tabs:
            assert str(sample_static_block.pk) in tab[1]

    @pytest.mark.django_db
    def test_get_tabs_handles_special_characters_in_search_query(self, mock_request, sample_static_block):
        """Test that _get_tabs handles special characters in search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "test & search"}
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "q=test+%26+search" in tabs[0][1]
        assert "q=test+%26+search" in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_handles_unicode_in_search_query(self, mock_request, sample_static_block):
        """Test that _get_tabs handles unicode in search query."""
        mixin = StaticBlockTabMixin()
        mock_request.GET = {"q": "tëst søarch"}
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "q=" in tabs[0][1]
        assert "q=" in tabs[1][1]

    @pytest.mark.django_db
    def test_get_tabs_handles_long_search_query(self, mock_request, sample_static_block):
        """Test that _get_tabs handles long search query."""
        mixin = StaticBlockTabMixin()
        long_query = "a" * 1000
        mock_request.GET = {"q": long_query}
        mixin.request = mock_request
        mixin.kwargs = {"id": sample_static_block.id}

        tabs = mixin._get_tabs(sample_static_block)

        assert "q=" in tabs[0][1]
        assert "q=" in tabs[1][1]
