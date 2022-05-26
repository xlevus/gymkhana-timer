from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from gk.leaderboard.models import Course, Time
from gk.rider.models import Rider
from gk.timer.forms import TimerForm

from .models import Timer

# Create your views here.


class TimerView(LoginRequiredMixin, DetailView):
    object: Course

    model = Course
    template_name = "timer/timer.html"

    def get_riders(self):
        return Rider.objects.all()

    def get_rider_names(self):
        return (
            self.object.times.filter(create_date__date=date.today())
            .exclude(rider_name="")
            .values("rider_name")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            names=self.get_rider_names(), riders=self.get_riders(), **kwargs
        )

    def get_timer(self) -> Timer:
        try:
            timer = Timer.objects.get(owner=self.request.user, secret="")
        except Timer.DoesNotExist:
            timer = Timer.objects.create(
                owner=self.request.user,
                name="Web Timer",
                secret="_",
            )
        return timer

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = TimerForm(request.POST)
        if form.is_valid():
            time = form.save(self.object, self.get_timer())
            messages.add_message(
                request=request,
                level=messages.INFO,
                message=_("Saved time {}").format(time),
            )
        else:
            import pdb

            pdb.set_trace()
            messages.add_message(
                request=request, level=messages.ERROR, message=_("Unable to save time.")
            )
        return HttpResponseRedirect(request.path)
