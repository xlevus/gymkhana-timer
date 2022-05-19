from django.urls import include, path
from django_registration.backends.one_step.views import RegistrationView

from .forms import RegistrationForm

urlpatterns = [
    # ... other URL patterns here
    path(
        "register/",
        RegistrationView.as_view(form_class=RegistrationForm),
        name="rider-register",
    ),
    path("", include("django_registration.backends.activation.urls")),
    # ... more URL patterns
]
