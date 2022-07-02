from django import forms
from gk.rider.models import Rider


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Rider
        fields = [
            "_display_name",
        ]
