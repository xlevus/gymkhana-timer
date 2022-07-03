from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Rider


class RiderAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Profile", {"fields": ["_display_name"]}),)


admin.site.register(Rider, RiderAdmin)

# Register your models here.
