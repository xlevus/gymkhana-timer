from django.contrib import admin

from . import models


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")

    prepopulated_fields = {
        "slug": ("name",),
    }


class TimeAdmin(admin.ModelAdmin):
    list_display = ("course", "rider", "rider_name", "time_ms", "penalty_ms", "total_ms", "run_date")


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Time, TimeAdmin)
