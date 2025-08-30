from django import forms


class FileUploadForm(forms.Form):
    """Simple form for file uploads in FilesView."""

    pass  # No form fields needed - we handle file uploads directly in the view
