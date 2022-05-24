from django.contrib import admin

from . import models


class TimerAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "created"]


admin.site.register(models.Timer, TimerAdmin)

# Register your models here.
