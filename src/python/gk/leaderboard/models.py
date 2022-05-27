from django.conf import settings
from django.db import models
from django.db.models import F, Window
from django.db.models.functions import RowNumber


class Course(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def best_times(self):
        ranks = [
            pk
            for (pk, rank) in Time.objects.filter(course=self)
            .annotate(
                rank=Window(
                    expression=RowNumber(),
                    partition_by=[F("group_id")],
                    order_by=[F("time_ms").asc()],
                )
            )
            .values_list("pk", "rank")
            if rank == 1
        ]
        return (
            Time.objects.filter(pk__in=ranks)
            .order_by("time_ms")
            .select_related("rider")
        )


class Time(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="times")
    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="times",
    )
    bike = models.CharField(max_length=128, blank=True)
    rider_name = models.CharField(max_length=128, blank=True)
    time_ms = models.IntegerField()
    run_date = models.DateTimeField()
    video_url = models.URLField(blank=True)

    group_id = models.CharField(max_length=128, blank=True)

    timer = models.ForeignKey(
        "timer.Timer", blank=True, null=True, on_delete=models.CASCADE
    )
    create_date = models.DateTimeField(auto_now_add=True)

    class Options:
        ordering = ["run_date"]

    @property
    def display_name(self):
        if self.rider:
            return str(self.rider)
        return self.rider_name

    def __str__(self):
        return f"{self.display_name}: {self.time}"

    def save(self, *args, **kwargs):
        if self.rider_id:
            self.group_id = f"__U{self.rider_id}"
        else:
            self.group_id = f"__R{self.rider_name}"

        super().save(*args, **kwargs)

    @property
    def time(self) -> str:
        millis = self.time_ms % 1000
        seconds = (self.time_ms // 1000) % 60
        minutes = self.time_ms // (1000 * 60)
        return f"{minutes:02}:{seconds:02}.{millis:03}"
