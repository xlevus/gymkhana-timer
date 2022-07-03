from allauth.account import views
from django.urls import include, path
from gk.rider import views

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="rider-profile"),
    path("profile/delete/", views.DeleteProfileView.as_view(), name="rider-delete-profile"),
    path("profile/", include("allauth.urls")),
]
