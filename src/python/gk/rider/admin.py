from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Rider

admin.site.register(Rider, UserAdmin)

# Register your models here.
