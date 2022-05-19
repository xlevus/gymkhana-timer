from django_registration.forms import RegistrationForm as BaseRegistrationForm

from . import models


class RegistrationForm(BaseRegistrationForm):
    class Meta(BaseRegistrationForm.Meta):
        model = models.Rider
