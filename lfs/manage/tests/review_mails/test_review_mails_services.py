import pytest
from unittest.mock import Mock
from django.test import RequestFactory

from lfs.marketing.models import OrderRatingMail
from lfs.manage.review_mails.services import RatingMailService


@pytest.fixture
def mock_request():
    """Create a mock request for testing."""
    factory = RequestFactory()
    return factory.get("/")


@pytest.fixture
def rating_mail_service(mock_request, monkeypatch):
    """Create a RatingMailService instance for testing."""
    # Mock ContentType
    mock_ctype = Mock()
    mock_ctype.id = 1
    monkeypatch.setattr("lfs.manage.review_mails.services.ContentType.objects.get_for_model", lambda x: mock_ctype)

    # Mock Site
    mock_site = Mock()
    mock_site.id = 1
    monkeypatch.setattr("lfs.manage.review_mails.services.Site.objects.get", lambda **kwargs: mock_site)

    # Mock Shop
    mock_shop = Mock()
    mock_shop.name = "Test Shop"
    mock_shop.from_email = "test@shop.com"
    mock_shop.get_notification_emails = lambda: ["admin@shop.com"]
    monkeypatch.setattr("lfs.manage.review_mails.services.lfs.core.utils.get_default_shop", lambda: mock_shop)

    return RatingMailService(request=mock_request)


class TestRatingMailService:
    """Test cases for RatingMailService."""

    def test_should_initialize_with_correct_attributes(self, rating_mail_service):
        """Test that service initializes with correct attributes."""
        assert rating_mail_service.ctype.id == 1
        assert "http://" in rating_mail_service.site  # Just check it contains http://
        assert rating_mail_service.shop.name == "Test Shop"

    def test_should_return_eligible_orders_when_no_rating_mails_sent(self, rating_mail_service, monkeypatch):
        """Test that service returns orders that haven't had rating mails sent."""
        # Arrange
        mock_order1 = Mock()
        mock_order2 = Mock()
        monkeypatch.setattr(
            "lfs.manage.review_mails.services.lfs.marketing.utils.get_orders", lambda: [mock_order1, mock_order2]
        )
        monkeypatch.setattr(
            "lfs.manage.review_mails.services.OrderRatingMail.objects.get",
            Mock(side_effect=OrderRatingMail.DoesNotExist),
        )

        # Act
        eligible_orders = rating_mail_service.get_orders_for_rating_mails()

        # Assert
        assert len(eligible_orders) == 2
        assert mock_order1 in eligible_orders
        assert mock_order2 in eligible_orders

    def test_should_exclude_orders_with_existing_rating_mails(self, rating_mail_service, monkeypatch):
        """Test that service excludes orders that already have rating mails sent."""
        # Arrange
        mock_order1 = Mock()
        mock_order2 = Mock()
        monkeypatch.setattr(
            "lfs.manage.review_mails.services.lfs.marketing.utils.get_orders", lambda: [mock_order1, mock_order2]
        )

        def mock_get_side_effect(order):
            if order == mock_order1:
                return Mock()  # OrderRatingMail exists
            else:
                raise OrderRatingMail.DoesNotExist

        monkeypatch.setattr(
            "lfs.manage.review_mails.services.OrderRatingMail.objects.get", Mock(side_effect=mock_get_side_effect)
        )

        # Act
        eligible_orders = rating_mail_service.get_orders_for_rating_mails()

        # Assert
        assert len(eligible_orders) == 1
        assert mock_order2 in eligible_orders
        assert mock_order1 not in eligible_orders

    def test_should_generate_email_content_with_correct_context(self, rating_mail_service, monkeypatch):
        """Test that service generates email content with correct context."""
        # Arrange
        mock_order = Mock()
        mock_order_item = Mock()
        mock_product = Mock()
        mock_product.id = 123
        mock_product.name = "Test Product"
        mock_product.is_variant.return_value = False
        mock_order_item.product = mock_product
        mock_order.items.all.return_value = [mock_order_item]

        mock_render = Mock()
        mock_render.side_effect = ["text_content", "html_content"]
        monkeypatch.setattr("lfs.manage.review_mails.services.render_to_string", mock_render)

        # Act
        content = rating_mail_service.generate_email_content(mock_order)

        # Assert
        assert content["text"] == "text_content"
        assert content["html"] == "html_content"
        assert len(content["order_items"]) == 1
        assert content["order_items"][0]["product_id"] == 123
        assert content["order_items"][0]["product_name"] == "Test Product"

        # Verify render_to_string was called with correct context
        assert mock_render.call_count == 2

    def test_should_handle_variant_products_correctly(self, rating_mail_service, monkeypatch):
        """Test that service handles variant products by using parent product."""
        # Arrange
        mock_order = Mock()
        mock_order_item = Mock()
        mock_variant = Mock()
        mock_parent = Mock()
        mock_parent.id = 456
        mock_parent.name = "Parent Product"
        mock_variant.is_variant.return_value = True
        mock_variant.parent = mock_parent
        mock_order_item.product = mock_variant
        mock_order.items.all.return_value = [mock_order_item]

        mock_render = Mock()
        mock_render.side_effect = ["text_content", "html_content"]
        monkeypatch.setattr("lfs.manage.review_mails.services.render_to_string", mock_render)

        # Act
        content = rating_mail_service.generate_email_content(mock_order)

        # Assert
        assert content["order_items"][0]["product_id"] == 456
        assert content["order_items"][0]["product_name"] == "Parent Product"

    def test_should_send_rating_mail_successfully(self, rating_mail_service, monkeypatch):
        """Test that service sends rating mail successfully."""
        # Arrange
        mock_order = Mock()
        mock_order.customer_email = "customer@test.com"
        mock_order_item = Mock()
        mock_product = Mock()
        mock_product.id = 123
        mock_product.name = "Test Product"
        mock_product.is_variant.return_value = False
        mock_order_item.product = mock_product
        mock_order.items.all.return_value = [mock_order_item]

        mock_render = Mock()
        mock_render.side_effect = ["text_content", "html_content"]
        monkeypatch.setattr("lfs.manage.review_mails.services.render_to_string", mock_render)

        mock_email_instance = Mock()
        mock_email_class = Mock(return_value=mock_email_instance)
        monkeypatch.setattr("lfs.manage.review_mails.services.EmailMultiAlternatives", mock_email_class)

        mock_create = Mock()
        monkeypatch.setattr("lfs.manage.review_mails.services.OrderRatingMail.objects.create", mock_create)

        # Act
        result = rating_mail_service.send_rating_mail(mock_order)

        # Assert
        assert result is True
        mock_email_class.assert_called_once()
        mock_email_instance.attach_alternative.assert_called_once_with("html_content", "text/html")
        mock_email_instance.send.assert_called_once()
        mock_create.assert_called_once_with(order=mock_order)

    def test_should_send_test_mail_to_shop_emails(self, rating_mail_service, monkeypatch):
        """Test that service sends test mails to shop notification emails."""
        # Arrange
        mock_order = Mock()
        mock_order.customer_email = "customer@test.com"
        mock_order_item = Mock()
        mock_product = Mock()
        mock_product.id = 123
        mock_product.name = "Test Product"
        mock_product.is_variant.return_value = False
        mock_order_item.product = mock_product
        mock_order.items.all.return_value = [mock_order_item]

        mock_render = Mock()
        mock_render.side_effect = ["text_content", "html_content"]
        monkeypatch.setattr("lfs.manage.review_mails.services.render_to_string", mock_render)

        mock_email_instance = Mock()
        mock_email_class = Mock(return_value=mock_email_instance)
        monkeypatch.setattr("lfs.manage.review_mails.services.EmailMultiAlternatives", mock_email_class)

        mock_create = Mock()
        monkeypatch.setattr("lfs.manage.review_mails.services.OrderRatingMail.objects.create", mock_create)

        # Act
        rating_mail_service.send_rating_mail(mock_order, is_test=True)

        # Assert
        mock_email_class.assert_called_once()
        call_args = mock_email_class.call_args
        assert call_args[1]["to"] == ["admin@shop.com"]
        mock_create.assert_not_called()

    def test_should_include_bcc_when_requested(self, rating_mail_service, monkeypatch):
        """Test that service includes BCC when requested."""
        # Arrange
        mock_order = Mock()
        mock_order.customer_email = "customer@test.com"
        mock_order_item = Mock()
        mock_product = Mock()
        mock_product.id = 123
        mock_product.name = "Test Product"
        mock_product.is_variant.return_value = False
        mock_order_item.product = mock_product
        mock_order.items.all.return_value = [mock_order_item]

        mock_render = Mock()
        mock_render.side_effect = ["text_content", "html_content"]
        monkeypatch.setattr("lfs.manage.review_mails.services.render_to_string", mock_render)

        mock_email_instance = Mock()
        mock_email_class = Mock(return_value=mock_email_instance)
        monkeypatch.setattr("lfs.manage.review_mails.services.EmailMultiAlternatives", mock_email_class)

        mock_create = Mock()
        monkeypatch.setattr("lfs.manage.review_mails.services.OrderRatingMail.objects.create", mock_create)

        # Act
        rating_mail_service.send_rating_mail(mock_order, include_bcc=True)

        # Assert
        call_args = mock_email_class.call_args
        assert call_args[1]["bcc"] == ["admin@shop.com"]

    def test_should_send_batch_rating_mails_successfully(self, rating_mail_service, monkeypatch):
        """Test that service sends batch rating mails successfully."""
        # Arrange
        mock_order1 = Mock()
        mock_order2 = Mock()
        orders = [mock_order1, mock_order2]

        mock_send = Mock(return_value=True)
        monkeypatch.setattr(rating_mail_service, "send_rating_mail", mock_send)

        # Act
        sent_orders = rating_mail_service.send_rating_mails_batch(orders)

        # Assert
        assert len(sent_orders) == 2
        assert mock_send.call_count == 2
        assert mock_order1 in sent_orders
        assert mock_order2 in sent_orders

    def test_should_continue_batch_when_individual_mail_fails(self, rating_mail_service, monkeypatch):
        """Test that service continues batch processing when individual mail fails."""
        # Arrange
        mock_order1 = Mock()
        mock_order2 = Mock()
        orders = [mock_order1, mock_order2]

        def mock_send_side_effect(order, **kwargs):
            if order == mock_order1:
                raise Exception("Email failed")
            return True

        mock_send = Mock(side_effect=mock_send_side_effect)
        monkeypatch.setattr(rating_mail_service, "send_rating_mail", mock_send)

        # Act
        sent_orders = rating_mail_service.send_rating_mails_batch(orders)

        # Assert
        assert len(sent_orders) == 1
        assert mock_order2 in sent_orders
        assert mock_order1 not in sent_orders
