from django.contrib import admin

from . import models


class CourseAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ('name',),
    }


admin.site.register(models.Course, CourseAdmin)
