from collections import defaultdict

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from django.shortcuts import get_object_or_404, render

from . import models


def index(request):
    courses = [
        (course, course.best_times()[:5]) for course in models.Course.objects.all()
    ]

    return render(request, "index.html", {"courses": courses})


def course_detail(request, slug):
    course = get_object_or_404(models.Course, slug=slug)

    history = course.times.filter(course=course)[:50]

    return render(
        request,
        "course.html",
        {
            "course": course,
            "best_times": course.best_times(),
            "history": history,
        },
    )
