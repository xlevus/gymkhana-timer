"""gk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from gk.leaderboard import views as leaderboard
from gk.web import views as web

urlpatterns = [
    path("", leaderboard.IndexView.as_view(), name="index"),
    path("rider/", include("gk.rider.urls")),
    path(
        "series/<slug:series_slug>/course/<slug:slug>/",
        leaderboard.CourseDetailView.as_view(),
        name="course-detail",
    ),
    path(
        "course/<slug:slug>/",
        leaderboard.CourseDetailView.as_view(),
        name="course-detail",
    ),
    path("timer/", include("gk.timer.urls")),
    path("admin/", admin.site.urls),
    path("tos/", web.TermsOfServiceView.as_view(), name="terms-of-service"),
    path("privacy/", web.PrivacyPolicyView.as_view(), name="privacy-policy"),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
