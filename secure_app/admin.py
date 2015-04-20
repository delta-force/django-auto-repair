from django.contrib import admin

from .models import Request

class RequestAdmin(admin.ModelAdmin):
	list_display = ('timestamp', 'full_url', 'is_good')
	list_filter = ['is_good', 'full_url']

admin.site.register(Request, RequestAdmin)

