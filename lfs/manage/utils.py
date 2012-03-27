# django imports
from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth import load_backend
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.template.loader import render_to_string

# lfs imports
from lfs.catalog.models import Category
from lfs.catalog.models import Product

def cartesian_product(*seqin):
    """Calculates the cartesian product of given lists.
    """
    # Found in ASPN Cookbook
    def rloop(seqin, comb):
        if seqin:
            for item in seqin[0]:
                newcomb = comb + [item]
                for item in rloop(seqin[1:], newcomb):
                    yield item
        else:
            yield comb

    return rloop(seqin, [])

if __name__ == "__main__":
    for x in cartesian_product([u'5|11', u'7|15', u'6|12']):
        print x

def update_category_positions(category):
    """Updates the position of the children of the passed category.
    """
    i = 1
    for child in Category.objects.filter(parent=category):
        child.position = i
        child.save()
        i+= 2


def get_user_from_session_key(session_key):
    """Returns the user from the passed session_key.

    This is a workaround for jquery.upload, which is used to mass upload images
    and files.
    """
    try:
        session_engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        session_wrapper = session_engine.SessionStore(session_key)
        user_id = session_wrapper.get(SESSION_KEY)
        auth_backend = load_backend(session_wrapper.get(BACKEND_SESSION_KEY))
        if user_id and auth_backend:
            return auth_backend.get_user(user_id)
        else:
            return AnonymousUser()
    except AttributeError:
        return AnonymousUser()
