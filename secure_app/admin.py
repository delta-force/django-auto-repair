from django.contrib import admin

from .models import Request
from .models import Filter

class RequestAdmin(admin.ModelAdmin):
	list_display = ('timestamp', 'url_path', 'key', 'value', 'is_good')
	list_filter = ['is_good']

class FilterAdmin(admin.ModelAdmin):
        list_display = ('url_path','field_name', 'regex_filter')

admin.site.register(Filter, FilterAdmin)
admin.site.register(Request, RequestAdmin)

