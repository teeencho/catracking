from django.db import models


class TrackingRequest(models.Model):
    tracker = models.CharField(max_length=48)
    endpoint = models.CharField(max_length=2048)
    payload = models.TextField()
    response_code = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0} - {1}'.format(self.tracker, self.response_code)
