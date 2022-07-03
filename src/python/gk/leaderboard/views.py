from collections import defaultdict

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, TemplateView

from . import models


class IndexView(TemplateView):
    template_name = "index.html"

    def times(self):
        for course in models.Course.objects.all():
            qs = course.best_times()[:5]
            yield (course, qs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(times=self.times(), **kwargs)


class CourseDetailView(DetailView):
    object: models.Course
    model = models.Course

    def history(self):
        return self.object.times.order_by("-run_date")[:50]

    def best_times(self):
        return self.object.best_times()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            history=self.history(), best_times=self.best_times(), **kwargs
        )
