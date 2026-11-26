"""Validators for shop data entered in the management interface."""

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator
from django.utils.translation import gettext_lazy as _

_web_url = URLValidator(schemes=["http", "https"])
_email = EmailValidator()


def validate_link(value: str) -> None:
    """Accept an absolute http(s) URL, a path within the shop ("/page/imprint"), or "mailto:" with an address.

    Raises ValidationError for anything else, for example "javascript:", "//other-site", or a path without a leading
    slash, which would point somewhere else on every page.
    """
    if value.startswith("/") and not value.startswith("//"):
        return
    if value.startswith("mailto:"):
        address = value.removeprefix("mailto:").split("?", 1)[0]
        try:
            _email(address)
        except ValidationError:
            raise ValidationError(_("Enter an e-mail address after mailto:."), code="invalid") from None
        return
    try:
        _web_url(value)
    except ValidationError:
        raise ValidationError(
            _('Enter a URL (https://…), a path within the shop (/page/…), or "mailto:" with an address.'),
            code="invalid",
        ) from None
