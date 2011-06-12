# python imports
import hotshot
import hotshot.stats
import sys
import tempfile
from urlparse import urlparse
from cStringIO import StringIO

# django imports
from django import http
from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.http import HttpResponseServerError


class RedirectFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a redirect for non-404 responses.
        parsed_url = urlparse(request.get_full_path())
        path = parsed_url.path

        try:
            r = Redirect.objects.get(site__id__exact=settings.SITE_ID, old_path=path)
        except Redirect.DoesNotExist:
            r = None
        if r is None and settings.APPEND_SLASH:
            # Try removing the trailing slash.
            try:
                r = Redirect.objects.get(site__id__exact=settings.SITE_ID,
                    old_path=path[:path.rfind('/')] + path[path.rfind('/') + 1:])
            except Redirect.DoesNotExist:
                pass
        if r is not None:
            if r.new_path == '':
                return http.HttpResponseGone()
            new_path = r.new_path + "?" + parsed_url.query
            return http.HttpResponsePermanentRedirect(new_path)

        # No redirect was found. Return the response.
        return response


class ProfileMiddleware(object):
    """
    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode,
    but you really shouldn't add this middleware to any production configuration.
    * Only tested on Linux
    """
    def process_request(self, request):
        if 'prof' in request.GET:
            self.tmpfile = tempfile.NamedTemporaryFile()
            self.prof = hotshot.Profile(self.tmpfile.name)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if 'prof' in request.GET:
            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)

    def process_response(self, request, response):
        if 'prof' in request.GET:
            self.prof.close()

            out = StringIO()
            old_stdout = sys.stdout
            sys.stdout = out

            stats = hotshot.stats.load(self.tmpfile.name)
            # stats.strip_dirs()
            stats.sort_stats('cumulative', )
            # stats.sort_stats('time', )
            stats.print_stats()

            sys.stdout = old_stdout
            stats_str = out.getvalue()

            if response and response.content and stats_str:
                response.content = "<pre>" + stats_str + "</pre>"

        return response


class AJAXSimpleExceptionResponse:
    def process_exception(self, request, exception):
        if settings.DEBUG:
            if request.is_ajax():
                import sys
                import traceback
                (exc_type, exc_info, tb) = sys.exc_info()
                response = "%s\n" % exc_type.__name__
                response += "%s\n\n" % exc_info
                response += "TRACEBACK:\n"
                for tb in traceback.format_tb(tb):
                    response += "%s\n" % tb
                return HttpResponseServerError(response)
