from django.shortcuts import render

from . import models


def index(request):
    courses = models.Course.objects.all()
    return render(request, "index.html", {
        "courses": courses
    })