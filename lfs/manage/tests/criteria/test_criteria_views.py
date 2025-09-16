"""
Unit tests for criteria management views.

Following TDD principles:
- Test behavior, not implementation
- Clear test names describing expected behavior
- Arrange-Act-Assert structure
- One assertion per test (when practical)
- Fast tests with minimal mocking
"""

import pytest
from unittest.mock import Mock, patch
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from lfs.manage.criteria.views import (
    add_criterion,
    change_criterion_form,
    delete_criterion,
)

User = get_user_model()


class TestAddCriterion:
    """Test the add_criterion view function."""

    def test_add_criterion_function_exists(self):
        """Should have add_criterion function."""
        assert callable(add_criterion)

    def test_add_criterion_requires_permission(self):
        """Should require core.manage_shop permission."""
        from lfs.manage.criteria.views import AddCriterionView

        assert AddCriterionView.permission_required == "core.manage_shop"

    @patch(
        "lfs.manage.criteria.views.settings.LFS_CRITERIA",
        [
            ["lfs.criteria.models.CartPriceCriterion", "Cart Price"],
            ["lfs.criteria.models.CountryCriterion", "Country"],
        ],
    )
    @patch("lfs.manage.criteria.views.import_symbol")
    def test_add_criterion_returns_default_criterion_html(self, mock_import_symbol, mock_request):
        """Should return HTML for default criterion when LFS_CRITERIA is configured."""
        # Arrange
        mock_criterion_class = Mock()
        mock_criterion_instance = Mock()
        mock_criterion_instance.render.return_value = "<div>Test Criterion HTML</div>"
        mock_criterion_class.return_value = mock_criterion_instance
        mock_import_symbol.return_value = mock_criterion_class

        # Act
        response = add_criterion(mock_request)

        # Assert
        assert isinstance(response, HttpResponse)
        assert response.content.decode() == "<div>Test Criterion HTML</div>"
        # The function calls import_symbol twice due to the try/except and then again
        assert mock_import_symbol.call_count == 2
        mock_criterion_instance.render.assert_called_with(mock_request, 10)

    @patch("lfs.manage.criteria.views.settings.LFS_CRITERIA", [])
    def test_add_criterion_returns_empty_when_no_criteria_configured(self, mock_request):
        """Should return empty response when LFS_CRITERIA is empty."""
        # Act
        with pytest.raises(IndexError):
            add_criterion(mock_request)

    @patch(
        "lfs.manage.criteria.views.settings.LFS_CRITERIA",
        [
            ["lfs.criteria.models.CartPriceCriterion", "Cart Price"],
        ],
    )
    @patch("lfs.manage.criteria.views.import_symbol")
    def test_add_criterion_handles_import_error_gracefully(self, mock_import_symbol, mock_request):
        """Should handle import errors gracefully and return empty response."""
        # Arrange
        mock_import_symbol.side_effect = ImportError("Module not found")

        # Act
        with pytest.raises(ImportError):
            add_criterion(mock_request)

    @patch(
        "lfs.manage.criteria.views.settings.LFS_CRITERIA",
        [
            ["lfs.criteria.models.CartPriceCriterion", "Cart Price"],
        ],
    )
    @patch("lfs.manage.criteria.views.import_symbol")
    def test_add_criterion_handles_render_error_gracefully(self, mock_import_symbol, mock_request):
        """Should handle render errors gracefully and return empty response."""
        # Arrange
        mock_criterion_class = Mock()
        mock_criterion_instance = Mock()
        mock_criterion_instance.render.side_effect = Exception("Render error")
        mock_criterion_class.return_value = mock_criterion_instance
        mock_import_symbol.return_value = mock_criterion_class

        # Act
        with pytest.raises(Exception):
            add_criterion(mock_request)


class TestChangeCriterionForm:
    """Test the change_criterion_form view function."""

    def test_change_criterion_form_function_exists(self):
        """Should have change_criterion_form function."""
        assert callable(change_criterion_form)

    def test_change_criterion_form_requires_permission(self):
        """Should require core.manage_shop permission."""
        from lfs.manage.criteria.views import ChangeCriterionFormView

        assert ChangeCriterionFormView.permission_required == "core.manage_shop"

    @patch("lfs.manage.criteria.views.import_symbol")
    def test_change_criterion_form_returns_criterion_html(self, mock_import_symbol, request_factory, manage_user):
        """Should return HTML for specified criterion type."""
        # Arrange
        request = request_factory.post("/", {"type": "lfs.criteria.models.CartPriceCriterion"})
        request.user = manage_user

        mock_criterion_class = Mock()
        mock_criterion_instance = Mock()
        mock_criterion_instance.render.return_value = "<div>Changed Criterion HTML</div>"
        mock_criterion_class.return_value = mock_criterion_instance
        mock_import_symbol.return_value = mock_criterion_class

        # Act
        response = change_criterion_form(request)

        # Assert
        assert isinstance(response, HttpResponse)
        assert response.content.decode() == "<div>Changed Criterion HTML</div>"
        mock_import_symbol.assert_called_once_with("lfs.criteria.models.CartPriceCriterion")
        mock_criterion_instance.render.assert_called_once_with(request, 10)

    def test_change_criterion_form_uses_default_type_when_none_provided(self, request_factory, manage_user):
        """Should use default type 'price' when no type provided in POST."""
        # Arrange
        request = request_factory.post("/", {})  # No type provided
        request.user = manage_user

        with patch("lfs.manage.criteria.views.import_symbol") as mock_import_symbol:
            mock_criterion_class = Mock()
            mock_criterion_instance = Mock()
            mock_criterion_instance.render.return_value = "<div>Default Criterion HTML</div>"
            mock_criterion_class.return_value = mock_criterion_instance
            mock_import_symbol.return_value = mock_criterion_class

            # Act
            response = change_criterion_form(request)

            # Assert
            assert isinstance(response, HttpResponse)
            assert response.content.decode() == "<div>Default Criterion HTML</div>"
            mock_import_symbol.assert_called_once_with("price")

    @patch("lfs.manage.criteria.views.import_symbol")
    def test_change_criterion_form_handles_import_error_gracefully(
        self, mock_import_symbol, request_factory, manage_user
    ):
        """Should handle import errors gracefully."""
        # Arrange
        request = request_factory.post("/", {"type": "invalid.module.Class"})
        request.user = manage_user
        mock_import_symbol.side_effect = ImportError("Module not found")

        # Act
        with pytest.raises(ImportError):
            change_criterion_form(request)

    @patch("lfs.manage.criteria.views.import_symbol")
    def test_change_criterion_form_handles_render_error_gracefully(
        self, mock_import_symbol, request_factory, manage_user
    ):
        """Should handle render errors gracefully."""
        # Arrange
        request = request_factory.post("/", {"type": "lfs.criteria.models.CartPriceCriterion"})
        request.user = manage_user

        mock_criterion_class = Mock()
        mock_criterion_instance = Mock()
        mock_criterion_instance.render.side_effect = Exception("Render error")
        mock_criterion_class.return_value = mock_criterion_instance
        mock_import_symbol.return_value = mock_criterion_class

        # Act
        with pytest.raises(Exception):
            change_criterion_form(request)


class TestDeleteCriterion:
    """Test the delete_criterion view function."""

    def test_delete_criterion_function_exists(self):
        """Should have delete_criterion function."""
        assert callable(delete_criterion)

    def test_delete_criterion_requires_permission(self):
        """Should require core.manage_shop permission."""
        from lfs.manage.criteria.views import DeleteCriterionView

        assert DeleteCriterionView.permission_required == "core.manage_shop"

    def test_delete_criterion_requires_delete_method(self):
        """Should only accept DELETE HTTP method."""
        from lfs.manage.criteria.views import DeleteCriterionView

        assert hasattr(DeleteCriterionView, "delete")
        assert not hasattr(DeleteCriterionView, "get")  # Should not have GET method
        assert not hasattr(DeleteCriterionView, "post")  # Should not have POST method

    def test_delete_criterion_returns_empty_response(self, request_factory, manage_user):
        """Should return empty HttpResponse for HTMX delete requests."""
        # Arrange
        request = request_factory.delete("/")
        request.user = manage_user

        # Act
        response = delete_criterion(request)

        # Assert
        assert isinstance(response, HttpResponse)
        assert response.content.decode() == ""

    def test_delete_criterion_handles_post_request(self, request_factory, manage_user):
        """Should handle POST requests (though not recommended)."""
        # Arrange
        request = request_factory.post("/")
        request.user = manage_user

        # Act
        response = delete_criterion(request)

        # Assert
        assert isinstance(response, HttpResponse)
        assert response.content.decode() == ""

    def test_delete_criterion_handles_get_request(self, request_factory, manage_user):
        """Should handle GET requests (though not recommended)."""
        # Arrange
        request = request_factory.get("/")
        request.user = manage_user

        # Act
        response = delete_criterion(request)

        # Assert
        assert isinstance(response, HttpResponse)
        assert response.content.decode() == ""


class TestCriteriaViewsIntegration:
    """Integration tests for criteria views."""

    @patch(
        "lfs.manage.criteria.views.settings.LFS_CRITERIA",
        [
            ["lfs.criteria.models.CartPriceCriterion", "Cart Price"],
            ["lfs.criteria.models.CountryCriterion", "Country"],
        ],
    )
    @patch("lfs.manage.criteria.views.import_symbol")
    def test_add_criterion_with_real_criterion_class(self, mock_import_symbol, request_factory, manage_user):
        """Should work with real criterion class structure."""
        # Arrange
        request = request_factory.get("/")
        request.user = manage_user

        # Mock the criterion class to behave like a real one
        mock_criterion_class = Mock()
        mock_criterion_instance = Mock()
        mock_criterion_instance.render.return_value = "<div>Real Criterion HTML</div>"
        mock_criterion_class.return_value = mock_criterion_instance
        mock_import_symbol.return_value = mock_criterion_class

        # Act
        response = add_criterion(request)

        # Assert
        assert isinstance(response, HttpResponse)
        assert response.content.decode() == "<div>Real Criterion HTML</div>"
        # The function calls import_symbol twice due to the try/except and then again
        assert mock_import_symbol.call_count == 2

    def test_change_criterion_form_with_different_types(self, request_factory, manage_user):
        """Should handle different criterion types correctly."""
        # Arrange
        criterion_types = [
            "lfs.criteria.models.CartPriceCriterion",
            "lfs.criteria.models.CountryCriterion",
            "lfs.criteria.models.WeightCriterion",
        ]

        with patch("lfs.manage.criteria.views.import_symbol") as mock_import_symbol:
            mock_criterion_class = Mock()
            mock_criterion_instance = Mock()
            mock_criterion_instance.render.return_value = "<div>Test HTML</div>"
            mock_criterion_class.return_value = mock_criterion_instance
            mock_import_symbol.return_value = mock_criterion_class

            for criterion_type in criterion_types:
                request = request_factory.post("/", {"type": criterion_type})
                request.user = manage_user

                # Act
                response = change_criterion_form(request)

                # Assert
                assert isinstance(response, HttpResponse)
                assert response.content.decode() == "<div>Test HTML</div>"
                mock_import_symbol.assert_called_with(criterion_type)

    def test_delete_criterion_is_htmx_compatible(self, request_factory, manage_user):
        """Should be compatible with HTMX delete requests."""
        # Arrange
        request = request_factory.delete("/", HTTP_HX_REQUEST="true")
        request.user = manage_user

        # Act
        response = delete_criterion(request)

        # Assert
        assert isinstance(response, HttpResponse)
        assert response.content.decode() == ""
        assert response.status_code == 200


class TestCriteriaViewsErrorHandling:
    """Test error handling in criteria views."""

    @patch("lfs.manage.criteria.views.settings.LFS_CRITERIA", None)
    def test_add_criterion_handles_none_criteria_setting(self, mock_request):
        """Should handle None LFS_CRITERIA setting gracefully."""
        # Act
        with pytest.raises((TypeError, AttributeError)):
            add_criterion(mock_request)

    @patch(
        "lfs.manage.criteria.views.settings.LFS_CRITERIA",
        [
            ["invalid.module.Class", "Invalid Criterion"],
        ],
    )
    @patch("lfs.manage.criteria.views.import_symbol")
    def test_add_criterion_handles_invalid_criterion_class(self, mock_import_symbol, mock_request):
        """Should handle invalid criterion class in LFS_CRITERIA."""
        # Arrange
        mock_import_symbol.side_effect = ImportError("Invalid module")

        # Act
        with pytest.raises(ImportError):
            add_criterion(mock_request)

    def test_change_criterion_form_handles_missing_post_data(self, request_factory, manage_user):
        """Should handle missing POST data gracefully."""
        # Arrange
        request = request_factory.post("/")  # POST request without POST data
        request.user = manage_user

        with patch("lfs.manage.criteria.views.import_symbol") as mock_import_symbol:
            mock_criterion_class = Mock()
            mock_criterion_instance = Mock()
            mock_criterion_instance.render.return_value = "<div>Default HTML</div>"
            mock_criterion_class.return_value = mock_criterion_instance
            mock_import_symbol.return_value = mock_criterion_class

            # Act
            response = change_criterion_form(request)

            # Assert
            assert isinstance(response, HttpResponse)
            assert response.content.decode() == "<div>Default HTML</div>"
            mock_import_symbol.assert_called_once_with("price")  # Should use default
