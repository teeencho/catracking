from django.contrib import admin

from catracking.models import TrackingRequest


class TrackingRequestAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'endpoint', 'response_code', 'created')


admin.site.register(TrackingRequest, TrackingRequestAdmin)
