from datetime import datetime

from django import forms
from gk.leaderboard.models import Course, Time
from gk.rider.models import Rider
from gk.timer.models import Timer


class TimerForm(forms.Form):
    time_ms = forms.IntegerField(required=True)
    rider = forms.ModelChoiceField(Rider.objects, required=False)
    rider_name = forms.CharField(required=False)
    new_rider_name = forms.CharField(required=False)

    def save(self, course: Course, timer: Timer) -> Time:
        return Time.objects.create(
            course=course,
            rider=self.cleaned_data["rider"],
            rider_name=(
                self.cleaned_data["rider_name"] or self.cleaned_data["new_rider_name"]
            ),
            time_ms=self.cleaned_data["time_ms"],
            run_date=datetime.utcnow(),
        )
