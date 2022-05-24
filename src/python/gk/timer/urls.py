from django.urls import path

from .views import TimerView

urlpatterns = [
    path("<slug:slug>/", TimerView.as_view(), name="course_timer"),
]
