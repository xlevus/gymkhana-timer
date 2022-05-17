from collections import defaultdict

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from django.shortcuts import render

from . import models


def index(request):
    courses = []

    for course in models.Course.objects.all():
        ranks = [
            pk
            for (pk, rank) in models.Time.objects.filter(course=course)
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
        times = (
            models.Time.objects.filter(pk__in=ranks)
            .order_by("time_ms")
            .select_related("user")
        )
        courses.append((course, times))

    return render(request, "index.html", {"courses": courses})
