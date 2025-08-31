"""
Management view mixins for common functionality.
"""


class DirectDeleteMixin:
    """
    Mixin that makes DeleteView delete directly on GET without confirmation.
    
    This mixin bypasses Django's default confirmation template for DeleteView
    and directly calls the delete() method when a GET request is made.
    Useful for delete operations that are already confirmed via modals or other UI.
    """
    
    def get(self, request, *args, **kwargs):
        """Handle GET request - delete directly without confirmation."""
        return self.delete(request, *args, **kwargs)
