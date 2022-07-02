from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import UpdateView
from gk.rider import forms, models


class ProfileView(LoginRequiredMixin, UpdateView):
    model = models.Rider
    form_class = forms.ProfileForm
    template_name = "account/profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self) -> str:
        messages.add_message(
            self.request,
            messages.INFO,
            _("Successfully updated your profile."),
        )
        return reverse("rider-profile")
