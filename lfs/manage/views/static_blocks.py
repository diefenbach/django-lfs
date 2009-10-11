# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.utils
from lfs.catalog.models import StaticBlock

class StaticBlockForm(ModelForm):
    """Form to add and edit a static block.
    """
    class Meta:
        model = StaticBlock

@permission_required("manage_shop", login_url="/login/")
def manage_static_blocks(request):
    """Dispatches to the first static block or to the add static block form.
    """
    try:
        sb = StaticBlock.objects.all()[0]
        url = reverse("lfs_manage_static_block", kwargs={"id": sb.id})
    except IndexError:
        url = reverse("lfs_add_static_block")
    
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")
def manage_static_block(request, id, template_name="manage/static_block/static_block.html"):
    """Displays the main form to manage static blocks.
    """
    sb = get_object_or_404(StaticBlock, pk=id)
    if request.method == "POST":
        form = StaticBlockForm(instance=sb, data=request.POST)
        if form.is_valid():
            form.save()
            return lfs.core.utils.set_message_cookie(
                url = reverse("lfs_manage_static_block", kwargs={"id" : sb.id}),
                msg = _(u"Static block has been saved."),
            )            
    else:
        form = StaticBlockForm(instance=sb)
        
    return render_to_response(template_name, RequestContext(request, {
        "static_block" : sb,
        "static_blocks" : StaticBlock.objects.all(),
        "form" : form,
        "current_id" : int(id),
    }))

@permission_required("manage_shop", login_url="/login/")    
def add_static_block(request, template_name="manage/static_block/add_static_block.html"):
    """Provides a form to add a new static block.
    """
    if request.method == "POST":
        form = StaticBlockForm(data=request.POST)
        if form.is_valid():
            new_sb = form.save()
            return lfs.core.utils.set_message_cookie(
                url = reverse("lfs_manage_static_block", kwargs={"id" : new_sb.id}),
                msg = _(u"Static block has been added."),
            )            
    else:
        form = StaticBlockForm()

    return render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "static_blocks" : StaticBlock.objects.all(),        
    }))

@permission_required("manage_shop", login_url="/login/")
def preview_static_block(request, id, template_name="manage/static_block/preview.html"):
    """Displays a preview of an static block
    """
    sb = get_object_or_404(StaticBlock, pk=id)

    return render_to_response(template_name, RequestContext(request, {
        "static_block" : sb,        
    }))

@permission_required("manage_shop", login_url="/login/")
def delete_static_block(request, id):
    """Deletes static block with passed id.
    """
    sb = get_object_or_404(StaticBlock, pk=id)
    
    # First we delete all referencing categories. Otherwise they would be 
    # deleted
    for category in sb.categories.all():
        category.static_block = None
        category.save()    
    sb.delete()
    
    return lfs.core.utils.set_message_cookie(
        url = reverse("lfs_manage_static_blocks"),
        msg = _(u"Static block has been deleted."),
    )