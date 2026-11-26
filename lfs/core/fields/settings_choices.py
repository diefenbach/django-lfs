"""Model fields whose choices come from the project's settings."""

from typing import Any

from django.db import models


class SettingsChoicesMixin:
    """Leave the choices and the default out of migrations, because they come from the project's settings.

    The fields keep both at runtime (forms, validation, ``get_FOO_display()``). In migrations they would freeze
    the settings of whoever generated them, and every shop with other settings would see a pending migration.
    Neither changes the database column, so migrations do not need them.
    """

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        """Return the field's description for migrations, without choices and default."""
        name, path, args, kwargs = super().deconstruct()  # type: ignore[misc]
        kwargs.pop("choices", None)
        kwargs.pop("default", None)
        return name, path, args, kwargs


class SettingsChoicesCharField(SettingsChoicesMixin, models.CharField):
    """A CharField whose choices (and default) come from the settings, e.g. price calculators or units."""


class SettingsChoicesPositiveSmallIntegerField(SettingsChoicesMixin, models.PositiveSmallIntegerField):
    """A PositiveSmallIntegerField whose choices come from the settings, e.g. order states or templates."""
