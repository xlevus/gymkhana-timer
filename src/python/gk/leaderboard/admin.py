from django.contrib import admin

from . import models


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")

    prepopulated_fields = {
        "slug": ("name",),
    }


class TimeAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "rider", "time_ms", "run_date")


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Time, TimeAdmin)
