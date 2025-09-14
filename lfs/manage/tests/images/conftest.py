"""
Pytest fixtures for Image testing.

Provides comprehensive test data and utilities for image management tests.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
import io

from lfs.catalog.models import Image

User = get_user_model()


# Common fixtures are now imported from the main conftest.py


@pytest.fixture
def test_image_file():
    """Create a test image file for uploads."""
    # Create a simple 100x100 red image
    image = PILImage.new("RGB", (100, 100), color="red")
    image_io = io.BytesIO()
    image.save(image_io, format="JPEG")
    image_io.seek(0)

    return SimpleUploadedFile("test_image.jpg", image_io.getvalue(), content_type="image/jpeg")


@pytest.fixture
def test_png_file():
    """Create a test PNG image file for uploads."""
    # Create a simple 50x50 blue image
    image = PILImage.new("RGB", (50, 50), color="blue")
    image_io = io.BytesIO()
    image.save(image_io, format="PNG")
    image_io.seek(0)

    return SimpleUploadedFile("test_image.png", image_io.getvalue(), content_type="image/png")


@pytest.fixture
def large_test_file():
    """Create a large test file for size validation."""
    # Create a 11MB file (larger than the 10MB limit)
    large_content = b"x" * (11 * 1024 * 1024)
    return SimpleUploadedFile("large_file.jpg", large_content, content_type="image/jpeg")


@pytest.fixture
def invalid_file():
    """Create an invalid file for type validation."""
    return SimpleUploadedFile("test.txt", b"not an image", content_type="text/plain")


@pytest.fixture
def image(db, test_image_file):
    """Image instance for testing."""
    image = Image(title="Test Image")
    image.image.save("test_image.jpg", test_image_file, save=True)
    return image


@pytest.fixture
def multiple_images(db, test_image_file, test_png_file):
    """Multiple Image instances for testing."""
    images = []

    # Create first image
    image1 = Image(title="Image 1")
    image1.image.save("test_image1.jpg", test_image_file, save=True)
    images.append(image1)

    # Create second image
    image2 = Image(title="Image 2")
    image2.image.save("test_image2.png", test_png_file, save=True)
    images.append(image2)

    # Create third image
    image3 = Image(title="Another Image")
    image3.image.save("test_image3.jpg", test_image_file, save=True)
    images.append(image3)

    return images


# Common fixtures (MockSession, mock_session, mock_request, htmx_request, enable_db_access_for_all_tests)
# are now imported from the main conftest.py
