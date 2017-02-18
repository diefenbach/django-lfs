from collections import deque
import datetime
from itertools import count
import locale
import sys
import urllib
import json
import time

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.shortcuts import render
from django.utils.http import cookie_date


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


def atof(value):
    """
    locale.atof() on unicode string fails in some environments, like Czech.
    """
    val = str(value)
    try:
        return float(val)
    except ValueError:
        try:
            return float(val.replace(',', '.'))
        except ValueError:
            pass

    if isinstance(value, unicode):
        value = value.encode("utf-8")
    return locale.atof(value)


def get_default_shop(request=None):
    """Returns the default shop.
    """
    from lfs.core.models import Shop
    if request:
        try:
            return request.shop
        except AttributeError:
            pass

    try:
        shop = Shop.objects.get(pk=1)
    except Shop.DoesNotExist:  # No guarantee that our shop will have pk=1 in postgres
        shop = Shop.objects.all()[0]

    if request:
        request.shop = shop

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


def import_symbol(symbol):
    """Imports symbol with given dotted name.
    """
    module_str, symbol_str = symbol.rsplit('.', 1)
    module = import_module(module_str)
    return getattr(module, symbol_str)


class MessageHttpResponseRedirect(HttpResponseRedirect):
    """
    Django's HttpResponseRedirect with a LFS message
    """
    def __init__(self, redirect_to, msg):
        HttpResponseRedirect.__init__(self, redirect_to)
        if msg:
            # We just keep the message two seconds.
            max_age = 2
            expires_time = time.time() + max_age
            expires = cookie_date(expires_time)

            self.set_cookie("message", lfs_quote(msg), max_age=max_age, expires=expires)


def render_to_message_response(*args, **kwargs):
    """
    Django's render_to_response with a LFS message.
    """
    msg = kwargs.get("msg")
    del kwargs["msg"]
    return set_message_to(render(*args, **kwargs), msg)


def set_message_to(response, msg):
    """Sets message cookie with passed message to passed response.
    """
    # We just keep the message two seconds.
    max_age = 2
    expires_time = time.time() + max_age
    expires = cookie_date(expires_time)
    if msg:
        response.set_cookie("message", lfs_quote(msg), max_age=max_age, expires=expires)
    return response


def set_message_cookie(url, msg):
    """Returns a HttpResponseRedirect object with passed url and set cookie
    ``message`` with passed message.
    """
    # We just keep the message two seconds.
    max_age = 2
    expires_time = time.time() + max_age
    expires = cookie_date(expires_time)

    response = HttpResponseRedirect(url)
    response.set_cookie("message", lfs_quote(msg), max_age=max_age, expires=expires)

    return response


def render_to_ajax_response(html=None, message=None):
    """Encodes given html and message to JSON and returns a HTTP response.
    """
    if html is None:
        html = []
    result = json.dumps(
        {"message": message, "html": html}, cls=LazyEncoder)

    return HttpResponse(result, content_type='application/json')


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
        redirect = Redirect.objects.get(old_path=path)
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
        redirect = Redirect.objects.get(old_path=path)
    except Redirect.DoesNotExist:
        return False
    else:
        redirect.delete()
        return True


def set_category_levels():
    """Sets the category levels based on the position in hierarchy.
    """
    from lfs.catalog.models import Category
    for category in Category.objects.all():
        category.level = len(category.get_parents()) + 1
        category.save()


def get_start_day(date):
    """Takes a string such as ``2009-07-23`` and returns datetime object of
    this day.
    """
    try:
        year, month, day = date.split("-")
        start = datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        return None
    return start


def get_end_day(date):
    """Takes a string such as ``2009-07-23`` and returns a datetime object with
    last valid second of this day: 23:59:59.
    """
    try:
        year, month, day = date.split("-")
    except ValueError:
        return None
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


class LazyEncoder(json.JSONEncoder):
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
        from lfs.catalog.models import Category
        # NOTE: We don't use the level attribute of the category but calculate
        # actual position of a category based on the current tree. In this way
        # the category tree always start with level 1 (even if we start with
        # category level 2) an the correct css is applied.
        level = 0
        categories = []
        for category in Category.objects.filter(level=self.start_level):

            if category.exclude_from_navigation:
                continue

            if self.currents and category in self.currents:
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
        from lfs.catalog.models import Category
        categories = []
        for category in Category.objects.filter(parent=category):

            if category.exclude_from_navigation:
                continue

            if self.currents and category in self.currents:
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


def define_page_range(current_page, total_pages, window=6):
    """ Returns range of pages that contains current page and few pages before and after it.

        @current_page - starts from 1
        @tota_pages - total number of pages
        @window - maximum number of pages shown with current page - should be even

        Examples (cucumber style):
             Given window = 6
             When current_page is 8
             and total_pages = 20
             Then I should see: 5 6 7 [8] 9 10 11

             Given window = 6
             When current_page is 8
             and total_pages = 9
             Then I should see: 3 4 5 6 7 [8] 9

             Given window = 6
             When current_page is 1
             and total_pages = 9
             Then I should see: [1] 2 3 4 5 6 7
    """
    # maximum length of page range is window + 1
    maxlen = window + 1
    page_range = deque(maxlen=maxlen)

    # minimum possible index is either: (current_page - window) or 1
    window_start = (current_page - window) if (current_page - window) > 0 else 1

    # maximum possible index is current_page + window or total_pages
    window_end = total_pages if (current_page + window) > total_pages else (current_page + window)

    # if we have enough pages then we should end at preffered end
    preffered_end = current_page + int(window / 2.0)

    for i in count(window_start):
        if i > window_end:
            # if we're on first page then our window will be [1] 2 3 4 5 6 7
            break
        elif i > preffered_end and len(page_range) == maxlen:
            # if we have enough pages already then stop at preffered_end
            break
        page_range.append(i)
    return list(page_range)


def lfs_pagination(request, current_page, url='', getparam='start'):
    """Prepare data for pagination

       @page - number of current page (starting from 1)
       @paginator - paginator object, eg. Paginator(contact_list, 25)
    """
    paginator = current_page.paginator
    current_page_no = current_page.number

    has_next = current_page.has_next()
    has_prev = current_page.has_previous()

    page_range = define_page_range(current_page.number, paginator.num_pages)

    first = 1
    last = paginator.num_pages

    if first in page_range:
        first = None

    if last in page_range:
        last = None

    to_return = {'page_range': page_range,
                 'current_page': current_page_no,
                 'total_pages': paginator.num_pages,
                 'has_next': has_next,
                 'has_prev': has_prev,
                 'next': current_page_no + 1,
                 'prev': current_page_no - 1,
                 'url': url,
                 'getparam': getparam,
                 'first_page': first,
                 'last_page': last,
                 'getvars': ''}

    getvars = request.GET.copy()
    if getparam in getvars:
        del getvars[getparam]
    if len(getvars.keys()) > 0:
        to_return['getvars'] = "&%s" % getvars.urlencode()
    return to_return
