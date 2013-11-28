# django imports
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns, url

# lfs.imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.core.utils import LazyEncoder

from django.views.generic.base import View


class SEOView(View):
    http_method_names = ['get', 'post']
    model_klass = None  # model that this view operates on
    form_klass = None  # SEO Form class (by default it's model form with fields: meta_[title|keywords|description])
    template_name = None  # template used to render SEO form

    @classmethod
    def get_seo_urlpattern(cls, model_klass, form_klass=None, template_name='manage/seo/seo.html'):
        """Prepare urlpattern for seo tab and give it a name based on content type of the model
        """
        ct = ContentType.objects.get_for_model(model_klass).pk
        view_obj = cls.as_view(form_klass=form_klass,
                               model_klass=model_klass,
                               template_name=template_name)

        return patterns('lfs.manage.seo.views',
                        url(r'^manage-seo/%s/(?P<id>\d*)/$' % ct,
                            permission_required("core.manage_shop")(view_obj),
                            name='lfs_manage_%s_seo' % ct),
                )

    def __init__(self, model_klass, form_klass=None, template_name='manage/seo/seo.html', *args, **kwargs):
        super(SEOView, self).__init__(*args, **kwargs)
        form_k = form_klass if form_klass else self.form_klass
        if not form_k:
            # if form_klass is not specified then prepare default model form for SEO management
            form_k = modelform_factory(model_klass,
                                       fields=("meta_title", "meta_keywords", "meta_description"))
        self.form_klass = form_k
        self.model_klass = model_klass
        self.template_name = template_name

        # each Model that defines seo fields has different url for seo management
        # By default this url differs by content type id
        ct = ContentType.objects.get_for_model(self.model_klass).pk
        self.urlname = 'lfs_manage_%s_seo' % ct

    def render(self, request, obj, form=None):
        """ Renders seo tab. Returns rendered HTML
        """
        if not form:
            form = self.form_klass(instance=obj)
        return render_to_string(self.template_name,
                                RequestContext(request, {
                                    "obj": obj,
                                    "urlname": self.urlname,
                                    "action_url": reverse(self.urlname, args=(obj.pk,)),
                                    "form": form
                                }))

    def render_to_response(self, form, message=''):
        """Prepare the output
        """
        seo_html = self.render(self.request, form.instance, form)
        return HttpResponse(simplejson.dumps({"seo": seo_html,
                                              "message": message
                                             }, cls=LazyEncoder), mimetype='application/json')

    def form_valid(self, form):
        """Handle successfull validation
        """
        form.save()
        message = _(u"SEO data has been saved.")
        return self.render_to_response(form, message)

    def form_invalid(self, form):
        """Handle validation errors
        """
        message = _(u"Please correct the indicated errors.")
        return self.render_to_response(form, message)

    def get(self, request, id):
        """ Handle GET request
        """
        obj = lfs_get_object_or_404(self.model_klass, pk=id)

        form = self.form_klass(instance=obj)
        return self.render_to_response(form)

    def post(self, request, id):
        """ Handle POST request
        """
        obj = lfs_get_object_or_404(self.model_klass, pk=id)

        form = self.form_klass(instance=obj, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
