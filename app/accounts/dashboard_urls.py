from django.urls import path

from .pages import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
]
