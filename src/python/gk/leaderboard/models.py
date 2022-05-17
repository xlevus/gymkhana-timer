from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Time(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="times")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="times"
    )
    bike = models.CharField(max_length=128, blank=True)
    rider = models.CharField(max_length=128, blank=True)
    time_ms = models.IntegerField()
    run_date = models.DateTimeField()
    video_url = models.URLField(blank=True)

    group_id = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.group_id} {self.time_ms}"

    def save(self, *args, **kwargs):
        if self.user:
            self.group_id = f"__U{self.user_id}"
        else:
            self.group_id = f"__R{self.rider}"

        super().save(*args, **kwargs)

    @property
    def time(self) -> str:
        millis = self.time_ms % 1000
        seconds = (self.time_ms // 1000) % 60
        minutes = self.time_ms // (1000 * 60)
        return f"{minutes:02}:{seconds:.0f}.{millis:03}"
