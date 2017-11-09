import arrow

from six.moves.urllib.parse import parse_qsl

from django.contrib import admin

from catracking.models import TrackingRequest


class TrackingRequestAdmin(admin.ModelAdmin):
    list_display = (
        'tracker', 'payloadify', 'endpoint', 'response_code', 'created')
    show_full_result_count = False

    def get_queryset(self, request):
        qs = super(TrackingRequestAdmin, self).get_queryset(request)
        five_hours_ago = arrow.utcnow().shift(hours=-5)
        return qs.filter(created__gte=five_hours_ago.datetime)

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
