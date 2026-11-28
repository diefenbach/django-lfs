"""
Management view mixins for common functionality.
"""


class DirectDeleteMixin:
    """
    Mixin for a DeleteView whose confirmation is a modal: it deletes on POST from that modal and refuses every other
    method with 405. A GET never deletes, so a link or an image cannot delete anything.

    On POST, Django's DeleteView calls ``form_valid()``, not ``delete()``; work that belongs to a deletion goes into
    ``form_valid()``.
    """

    http_method_names = ["post"]
