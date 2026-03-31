import pytest
from unittest.mock import Mock
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore

from lfs.manage.review_mails.views import RatingMailManageView, RatingMailSendView


@pytest.fixture
def user():
    """Create a test user with required permissions."""
    user = User.objects.create_user(username="testuser", password="testpass", email="test@example.com")
    return user


@pytest.fixture
def request_factory():
    """Create a request factory for testing."""
    return RequestFactory()


@pytest.fixture
def mock_request(request_factory, user):
    """Create a mock request with user and messages."""
    request = request_factory.get("/")
    request.user = user
    request.session = SessionStore()
    messages = FallbackStorage(request)
    request._messages = messages
    return request


class TestRatingMailManageView:
    """Test cases for RatingMailManageView."""

    def test_should_require_manage_shop_permission(self):
        """Test that view requires core.manage_shop permission."""
        assert RatingMailManageView.permission_required == "core.manage_shop"

    def test_should_use_correct_template(self):
        """Test that view uses correct template."""
        assert RatingMailManageView.template_name == "manage/review_mails/review_mails.html"

    @pytest.mark.django_db
    def test_should_get_eligible_orders_in_context(self, mock_request, monkeypatch):
        """Test that view includes eligible orders in context."""
        # Arrange
        mock_service = Mock()
        mock_orders = [Mock(), Mock()]
        mock_service.get_orders_for_rating_mails.return_value = mock_orders

        mock_service_class = Mock(return_value=mock_service)
        monkeypatch.setattr("lfs.manage.review_mails.views.RatingMailService", mock_service_class)

        view = RatingMailManageView()
        view.request = mock_request

        # Act
        context = view.get_context_data()

        # Assert
        assert "eligible_orders" in context
        assert context["eligible_orders"] == mock_orders
        mock_service_class.assert_called_once_with(request=mock_request)
        mock_service.get_orders_for_rating_mails.assert_called_once()


class TestRatingMailSendView:
    """Test cases for RatingMailSendView."""

    def test_should_require_manage_shop_permission(self):
        """Test that view requires core.manage_shop permission."""
        assert RatingMailSendView.permission_required == "core.manage_shop"

    def test_should_use_correct_template(self):
        """Test that view uses correct template."""
        assert RatingMailSendView.template_name == "manage/review_mails/review_mails.html"

    def test_should_have_success_message(self):
        """Test that view has correct success message."""
        assert RatingMailSendView.success_message == "Rating mails have been sent successfully."

    @pytest.mark.django_db
    def test_should_handle_post_request_successfully(self, request_factory, user, monkeypatch):
        """Test that view handles POST request successfully."""
        # Arrange
        mock_service = Mock()
        mock_orders = [Mock(), Mock()]
        mock_sent_orders = [Mock()]
        mock_service.get_orders_for_rating_mails.return_value = mock_orders
        mock_service.send_rating_mails_batch.return_value = mock_sent_orders

        mock_service_class = Mock(return_value=mock_service)
        monkeypatch.setattr("lfs.manage.review_mails.views.RatingMailService", mock_service_class)

        request = request_factory.post("/", {"test": "on", "bcc": "on"})
        request.user = user
        request.session = SessionStore()
        messages = FallbackStorage(request)
        request._messages = messages

        view = RatingMailSendView()
        view.request = request

        # Act
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        # Service is called twice: once in post() and once in get_context_data()
        assert mock_service_class.call_count == 2
        mock_service.get_orders_for_rating_mails.assert_called()
        mock_service.send_rating_mails_batch.assert_called_once_with(mock_orders, is_test=True, include_bcc=True)

    @pytest.mark.django_db
    def test_should_handle_post_without_test_mode(self, request_factory, user, monkeypatch):
        """Test that view handles POST without test mode."""
        # Arrange
        mock_service = Mock()
        mock_orders = [Mock()]
        mock_sent_orders = [Mock()]
        mock_service.get_orders_for_rating_mails.return_value = mock_orders
        mock_service.send_rating_mails_batch.return_value = mock_sent_orders

        mock_service_class = Mock(return_value=mock_service)
        monkeypatch.setattr("lfs.manage.review_mails.views.RatingMailService", mock_service_class)

        request = request_factory.post("/", {"bcc": "on"})  # No test checkbox
        request.user = user
        request.session = SessionStore()
        messages = FallbackStorage(request)
        request._messages = messages

        view = RatingMailSendView()
        view.request = request

        # Act
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        mock_service.send_rating_mails_batch.assert_called_once_with(mock_orders, is_test=False, include_bcc=True)

    @pytest.mark.django_db
    def test_should_handle_post_without_bcc(self, request_factory, user, monkeypatch):
        """Test that view handles POST without BCC."""
        # Arrange
        mock_service = Mock()
        mock_orders = [Mock()]
        mock_sent_orders = [Mock()]
        mock_service.get_orders_for_rating_mails.return_value = mock_orders
        mock_service.send_rating_mails_batch.return_value = mock_sent_orders

        mock_service_class = Mock(return_value=mock_service)
        monkeypatch.setattr("lfs.manage.review_mails.views.RatingMailService", mock_service_class)

        request = request_factory.post("/", {"test": "on"})  # No bcc checkbox
        request.user = user
        request.session = SessionStore()
        messages = FallbackStorage(request)
        request._messages = messages

        view = RatingMailSendView()
        view.request = request

        # Act
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        mock_service.send_rating_mails_batch.assert_called_once_with(mock_orders, is_test=True, include_bcc=False)

    @pytest.mark.django_db
    def test_should_include_correct_context_in_response(self, request_factory, user, monkeypatch):
        """Test that view includes correct context in response."""
        # Arrange
        mock_service = Mock()
        mock_orders = [Mock()]
        mock_sent_orders = [Mock()]
        mock_service.get_orders_for_rating_mails.return_value = mock_orders
        mock_service.send_rating_mails_batch.return_value = mock_sent_orders

        mock_service_class = Mock(return_value=mock_service)
        monkeypatch.setattr("lfs.manage.review_mails.views.RatingMailService", mock_service_class)

        request = request_factory.post("/", {"test": "on"})
        request.user = user
        request.session = SessionStore()
        messages = FallbackStorage(request)
        request._messages = messages

        view = RatingMailSendView()
        view.request = request

        # Act
        response = view.post(request)

        # Assert
        assert response.status_code == 200
        context = response.context_data
        assert context["display_orders_sent"] is True
        assert context["orders_sent"] == mock_sent_orders
        assert context["eligible_orders"] == mock_orders

    @pytest.mark.django_db
    def test_should_get_eligible_orders_in_get_context(self, mock_request, monkeypatch):
        """Test that view includes eligible orders in GET context."""
        # Arrange
        mock_service = Mock()
        mock_orders = [Mock(), Mock()]
        mock_service.get_orders_for_rating_mails.return_value = mock_orders

        mock_service_class = Mock(return_value=mock_service)
        monkeypatch.setattr("lfs.manage.review_mails.views.RatingMailService", mock_service_class)

        view = RatingMailSendView()
        view.request = mock_request

        # Act
        context = view.get_context_data()

        # Assert
        assert "eligible_orders" in context
        assert context["eligible_orders"] == mock_orders
        mock_service_class.assert_called_once_with(request=mock_request)
        mock_service.get_orders_for_rating_mails.assert_called_once()
