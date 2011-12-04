# django imports
from django.db import models

# lfs imports
from lfs.cart.utils import get_cart
from lfs.customer.utils import get_customer


class OrderNumberGenerator(models.Model):
    """This is the base class that order generator calculators should inherit
    from.
    """
    class Meta:
        abstract = True

    def init(self, request, order):
        """Initializes order number generator.
        """
        self.request = request
        self.order = order
        self.user = request.user
        self.customer = get_customer(request)
        self.cart = get_cart(request)

    def get_next(self, formatted=True):
        """Returns the next order number. Order number generators must
        implement this method in order to return

        **Parameters:**

        formatted
            If True the number will be returned within the stored format.

        **Return value**
            An order number which must be a character string.
        """
        raise NotImplementedError
