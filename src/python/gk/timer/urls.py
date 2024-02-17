from django.urls import path

from .views import TimerView

urlpatterns = [
    path("<slug:slug>/", TimerView.as_view(), name="course-timer"),
    path("<slug:series_slug>/<slug:slug>/", TimerView.as_view(), name="course-timer"),
]
