from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import UpdateView, DeleteView
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


class DeleteProfileView(LoginRequiredMixin, DeleteView):
    model = models.Rider
    template_name = "account/delete.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_time_count(self):
        return self.request.user.times.count()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            time_count=self.get_time_count(),
            **kwargs
        )

    def get_success_url(self) -> str:
        return reverse("index")