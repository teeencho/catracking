from six.moves.urllib.parse import parse_qsl

from django.contrib import admin

from catracking.models import TrackingRequest


class TrackingRequestAdmin(admin.ModelAdmin):
    list_display = (
        'tracker', 'payloadify', 'endpoint', 'response_code', 'created')
    show_full_result_count = False

    def payloadify(self, obj):
        """
        Ugly and dirty method to better visualize events in admin.
        Should be improved in future versions.
        """
        if obj.tracker == 'ga':
            values = dict(parse_qsl(obj.payload))
            event_type = values['t']
            if event_type == 'event':
                return 'event ({})'.format(', '.join(
                    [values['ec'], values['ea'], values['el']]))
        return ''
    payloadify.short_description = 'Friendly payload'


admin.site.register(TrackingRequest, TrackingRequestAdmin)
