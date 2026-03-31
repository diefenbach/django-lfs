from typing import List, Optional
import logging

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from lfs.catalog.models import Image

logger = logging.getLogger(__name__)


class MultipleFileInput(forms.FileInput):
    """Custom widget for multiple file uploads."""

    allow_multiple_selected = True

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({"multiple": True})
        super().__init__(attrs)


class ImageUploadForm(forms.Form):
    """Form for uploading multiple images."""

    files = forms.FileField(
        widget=MultipleFileInput(attrs={"accept": "image/*", "class": "form-control"}),
        label=_("Images"),
        help_text=_("Select one or more image files to upload."),
        required=True,
    )

    def clean_files(self):
        """Validate uploaded files."""
        files = self.files.getlist("files")
        if not files:
            raise ValidationError(_("At least one file must be selected."))

        # Validate each file
        for file in files:
            self._validate_image_file(file)

        return files

    def _validate_image_file(self, file):
        """Validate individual image file."""
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            raise ValidationError(
                _("File '%(filename)s' is too large. Maximum size is 10MB.") % {"filename": file.name}
            )

        # Check file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if hasattr(file, "content_type") and file.content_type not in allowed_types:
            raise ValidationError(
                _("File '%(filename)s' is not a valid image type. Allowed types: %(types)s")
                % {"filename": file.name, "types": ", ".join(allowed_types)}
            )

    def save(self) -> List[Image]:
        """Save uploaded images and return list of created Image objects."""
        if not self.is_valid():
            raise ValueError("Form is not valid")

        created_images = []
        files = self.cleaned_data["files"]

        for file in files:
            try:
                image = Image(title=file.name)
                image.image.save(file.name, file, save=True)
                created_images.append(image)
                logger.info("Successfully uploaded image: %s", file.name)
            except Exception as e:
                logger.error("Failed to upload image %s: %s", file.name, e)
                # Clean up any partially created image
                if image.pk:
                    image.delete()
                raise ValidationError(
                    _("Failed to upload image '%(filename)s': %(error)s") % {"filename": file.name, "error": str(e)}
                )

        return created_images


class ImageFilterForm(forms.Form):
    """Form for filtering images in the management interface."""

    q = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Search images..."), "class": "form-control"}),
        label=_("Search"),
        help_text=_("Search images by title."),
    )

    def get_queryset(self, base_queryset=None):
        """Get filtered queryset based on form data."""
        if base_queryset is None:
            base_queryset = Image.objects.filter(content_id=None)

        if not self.is_valid():
            return base_queryset

        query = self.cleaned_data.get("q", "").strip()
        if query:
            return base_queryset.filter(title__istartswith=query)

        return base_queryset


class ImageDeleteForm(forms.Form):
    """Form for deleting multiple images."""

    images = forms.ModelMultipleChoiceField(
        queryset=Image.objects.filter(content_id=None),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Images to delete"),
        help_text=_("Select images to delete. This action cannot be undone."),
    )

    def delete_selected(self) -> int:
        """Delete selected images and return count of deleted images."""
        if not self.is_valid():
            raise ValueError("Form is not valid")

        images = self.cleaned_data["images"]
        count = images.count()

        for image in images:
            logger.info("Deleting image: %s (ID: %s)", image.title, image.pk)

        images.delete()
        return count


class ImageBrowserForm(forms.Form):
    """Form for image browser selection."""

    ALIGNMENT_CHOICES = [
        ("inline", _("Inline")),
        ("left", _("Left")),
        ("right", _("Right")),
    ]

    image = forms.ModelChoiceField(
        queryset=Image.objects.filter(content_id=None), required=True, widget=forms.RadioSelect, label=_("Select Image")
    )

    alignment = forms.ChoiceField(
        choices=ALIGNMENT_CHOICES,
        initial="inline",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label=_("Alignment"),
    )

    size = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label=_("Size"),
        help_text=_("Leave empty for original size."),
    )

    def __init__(self, *args, **kwargs):
        """Initialize form with dynamic size choices."""
        super().__init__(*args, **kwargs)

        # Add size choices dynamically based on THUMBNAIL_SIZES
        from lfs.catalog.settings import THUMBNAIL_SIZES

        size_choices = [("", _("Original"))]
        for size in THUMBNAIL_SIZES:
            size_str = f"{size[0]}x{size[1]}"
            size_choices.append((size_str, size_str))

        self.fields["size"].widget = forms.Select(choices=size_choices, attrs={"class": "form-control"})

    def get_image_url(self) -> Optional[str]:
        """Get the URL for the selected image with specified size."""
        if not self.is_valid():
            return None

        image = self.cleaned_data["image"]
        size = self.cleaned_data.get("size", "")

        if not size:
            return image.image.url

        # Return sized image URL
        try:
            return getattr(image.image, f"url_{size}", image.image.url)
        except AttributeError:
            return image.image.url
