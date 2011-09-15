# python imports
import datetime
import sys
import urllib

# django imports
from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.contrib.redirects.models import Redirect

# lfs imports
import lfs.catalog.utils
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.models import Shop
from lfs.catalog.models import Category


def l10n_float(string):
    """Takes a country specfic decimal value as string and returns a float.
    """

    # TODO: Implement a proper transformation with babel or similar
    if settings.LANGUAGE_CODE == "de":
        string = string.replace(",", ".")

    try:
        return float(string)
    except ValueError:
        return 0.0


def get_default_shop():
    """Returns the default shop.
    """
    try:
        shop = Shop.objects.get(pk=1)
    except Shop.DoesNotExist, e:  # No guarantee that our shop will have pk=1 in postgres
        shop = Shop.objects.all()[0]
    return shop


def lfs_quote(string, encoding="utf-8"):
    """Encodes passed string to passed encoding before quoting with
    urllib.quote().
    """
    return urllib.quote(string.encode(encoding))


def import_module(module):
    """Imports module with given dotted name.
    """
    try:
        module = sys.modules[module]
    except KeyError:
        __import__(module)
        module = sys.modules[module]
    return module


def set_message_to(response, msg):
    """Sets message cookie with passed message to passed response.
    """
    # We just keep the message two seconds.
    max_age = 2
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() +
        datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")

    response.set_cookie("message", lfs_quote(msg), max_age=max_age, expires=expires)
    return response


def set_message_cookie(url, msg):
    """Returns a HttpResponseRedirect object with passed url and set cookie
    ``message`` with passed message.
    """
    # We just keep the message two seconds.
    max_age = 2
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() +
        datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")

    response = HttpResponseRedirect(url)
    response.set_cookie("message", lfs_quote(msg), max_age=max_age, expires=expires)

    return response


def render_to_ajax_response(html=[], message=None):
    """Encodes given html and message to JSON and returns a HTTP response.
    """
    result = simplejson.dumps(
        {"message": message, "html": html}, cls=LazyEncoder)

    return HttpResponse(result)


def get_current_categories(request, object):
    """Returns all current categories based on given request. Current
    categories are the current selected category and all parent categories of
    it.
    """
    if object and object.content_type == "category":
        parents = object.get_parents()
        current_categories = [object]
        current_categories.extend(parents)
    elif object and object.content_type == "product":
        current_categories = []
        category = object.get_current_category(request)
        while category:
            current_categories.append(category)
            category = category.parent
    else:
        current_categories = []

    return current_categories


def get_redirect_for(path):
    """Returns redirect path for the passed path.
    """
    try:
        redirect = Redirect.objects.get(
            site=settings.SITE_ID, old_path=path)
    except Redirect.DoesNotExist:
        return ""
    else:
        return redirect.new_path


def set_redirect_for(old_path, new_path):
    """Sets redirect path for the passed path.
    """
    try:
        redirect = Redirect.objects.get(site=settings.SITE_ID, old_path=old_path)
        redirect.new_path = new_path
        redirect.save()
    except Redirect.DoesNotExist:
        redirect = Redirect.objects.create(
            site_id=settings.SITE_ID, old_path=old_path, new_path=new_path)


def remove_redirect_for(path):
    """Removes the redirect path for given path.
    """
    try:
        redirect = Redirect.objects.get(site=settings.SITE_ID, old_path=path)
    except Redirect.DoesNotExist:
        return False
    else:
        redirect.delete()
        return True


def set_category_levels():
    """Sets the category levels based on the position in hierarchy.
    """
    for category in Category.objects.all():
        category.level = len(category.get_parents()) + 1
        category.save()


def get_start_day(date):
    """Takes a string such as ``2009-07-23`` and returns datetime object of
    this day.
    """
    year, month, day = date.split("-")
    start = datetime.datetime(int(year), int(month), int(day))
    return start


def get_end_day(date):
    """Takes a string such as ``2009-07-23`` and returns a datetime object with
    last valid second of this day: 23:59:59.
    """
    year, month, day = date.split("-")
    end = datetime.datetime(int(year), int(month), int(day))
    end = end + datetime.timedelta(1) - datetime.timedelta(microseconds=1)

    return end


def getLOL(objects, objects_per_row=3):
    """Returns a list of list of the passed objects with passed objects per
    row.
    """
    result = []
    row = []
    for i, object in enumerate(objects):
        row.append(object)
        if (i + 1) % objects_per_row == 0:
            result.append(row)
            row = []

    if len(row) > 0:
        result.append(row)

    return result


class LazyEncoder(simplejson.JSONEncoder):
    """Encodes django's lazy i18n strings.
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj


class CategoryTree(object):
    """Represents a category tree.
    """
    def __init__(self, currents, start_level, expand_level):
        self.currents = currents
        self.start_level = start_level
        self.expand_level = expand_level

    def get_category_tree(self):
        """Returns a category tree
        """
        # NOTE: We don't use the level attribute of the category but calculate
        # actual position of a category based on the current tree. In this way
        # the category tree always start with level 1 (even if we start with
        # category level 2) an the correct css is applied.
        level = 0
        categories = []
        for category in Category.objects.filter(level=self.start_level):

            if category.exclude_from_navigation:
                continue

            if (self.currents and category in self.currents):
                children = self._get_sub_tree(category, level + 1)
                is_current = True
            elif category.level <= self.expand_level:
                children = self._get_sub_tree(category, level + 1)
                is_current = False
            else:
                children = []
                is_current = False

            if self.start_level > 1:
                if category.parent in self.currents:
                    categories.append({
                        "category": category,
                        "children": children,
                        "level": level,
                        "is_current": is_current,
                    })
            else:
                categories.append({
                    "category": category,
                    "children": children,
                    "level": level,
                    "is_current": is_current,
                })

        return categories

    def _get_sub_tree(self, category, level):
        categories = []
        for category in Category.objects.filter(parent=category):

            if category.exclude_from_navigation:
                continue

            if (self.currents and category in self.currents):
                children = self._get_sub_tree(category, level + 1)
                is_current = True
            elif category.level <= self.expand_level:
                children = self._get_sub_tree(category, level + 1)
                is_current = False
            else:
                children = []
                is_current = False

            categories.append({
                "category": category,
                "children": children,
                "level": level,
                "is_current": is_current,
            })

        return categories
