# django imports
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

# djangorestframework imports
from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status

# lfs imports
from lfs.catalog.models import Category
from lfs.core.utils import set_category_levels


class CategorySortView(View):
    """
    API for sorting categories
    """
    @method_decorator(permission_required("core.manage_shop", login_url="/login/"))
    def post(self, request):
        """
        Handle POST requests containing category layout.
        """
        self.sort_categories(self.CONTENT.get('categories', ''))
        return HttpResponse("OK")

    def sort_categories(self, serialized_js):

        if serialized_js:
            #import ipdb; ipdb.set_trace()
            category_list = serialized_js.split('&')
            assert (isinstance(category_list, list))
            if len(category_list) > 0:
                pos = 10
                for cat_str in category_list:
                    child, parent_id = cat_str.split('=')
                    child_id = child[9:-1]  # category[2]
                    child_obj = Category.objects.get(pk=child_id)

                    parent_obj = None
                    if parent_id != 'root':
                        parent_obj = Category.objects.get(pk=parent_id)

                    child_obj.parent = parent_obj
                    child_obj.position = pos
                    child_obj.save()

                    pos = pos + 10
        set_category_levels()
