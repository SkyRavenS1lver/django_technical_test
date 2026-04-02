from django.urls import path

from .pages import DashboardView, LoginPageView, LogoutPageView, RegisterPageView

urlpatterns = [
    path("login/", LoginPageView.as_view(), name="login"),
    path("login/submit/", LoginPageView.as_view(), name="login-submit"),
    path("register/", RegisterPageView.as_view(), name="register"),
    path("register/submit/", RegisterPageView.as_view(), name="register-submit"),
    path("logout/", LogoutPageView.as_view(), name="logout"),
]
