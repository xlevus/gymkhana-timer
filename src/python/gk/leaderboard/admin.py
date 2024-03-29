from django.contrib import admin

from . import models


class SeriesAdmin(admin.ModelAdmin):
    fields = ("name", "slug", "order")
    list_display = ("name", "slug", "order")

    prepopulated_fields = {
        "slug": ("name",),
    }


class CourseAdmin(admin.ModelAdmin):
    fields = ["name", "slug", "series"]
    list_display = ("name", "slug", "series", "create_date", "modify_date")

    prepopulated_fields = {
        "slug": ("name",),
    }


class TimeAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "rider",
        "rider_name",
        "time_ms",
        "penalty_ms",
        "total_ms",
        "run_date",
    )


admin.site.register(models.Series, SeriesAdmin)
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Time, TimeAdmin)
