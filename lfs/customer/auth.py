# django imports
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """Authenticate against email addresses.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
        except (User.MultipleObjectsReturned, User.DoesNotExist):
            return None
        else:
            if user.check_password(password):
                return user
