import base64
import os

from django.conf import settings
from django.db import models


class Timer(models.Model):
    WEB_TIMER_SECRET = "_web_timer_"

    name = models.CharField(max_length=50)
    secret = models.CharField(max_length=64, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = base64.b64encode(os.urandom(128)).decode("ascii")[:64]
        return super().save(*args, **kwargs)
