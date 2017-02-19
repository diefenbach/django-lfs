# django imports
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SearchNotFound(models.Model):
  """
  A SearchNotFound is a query from a customer which no product response
  A SearchNotFound is only created from a search for a product not found because the livesearch will provide two many queries
  with product found and we need only the queries not found to complete our catalog. 
  **Attributes**
  user
    The user to which the cart belongs to
  session
    The session to which the cart belongs to
  creation_date
    The creation date of the cart

  A SearchNotFound can be assigned either to the current logged in User (in case
  the shop user is logged in) or to the current session (in case the shop
  user is not logged in).
  """
  user = models.ForeignKey(User, verbose_name=_(u"User"), blank=True, null=True)
  session = models.CharField(_(u"Session"), blank=True, max_length=100)
  creation_date = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
  query = models.CharField("Query not Found", blank=True, max_length=100)

  def __unicode__(self):
    return u"%s, %s" % (self.query, self.session)
