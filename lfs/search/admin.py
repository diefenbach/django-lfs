from django.contrib import admin
from lfs.search.models import SearchNotFound

class SearchNotFoundAdmin(admin.ModelAdmin):    
  list_display = ('creation_date', 'user', 'query', 'session' )
  search_fields = ('creation_date','user', 'query', 'session' )
    
admin.site.register(SearchNotFound, SearchNotFoundAdmin)
