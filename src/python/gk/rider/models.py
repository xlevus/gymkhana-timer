from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils.translation import gettext as _


class Rider(AbstractUser):
    _display_name = models.CharField(_("Display Name"), db_column="display_name", max_length=100, blank=True, default="")

    @property
    def display_name(self) -> str:
        return self._display_name or self.username

    @display_name.setter
    def display_name(self, value: str):
        self._display_name = value

    def __str__(self) -> str:
        return self.display_name