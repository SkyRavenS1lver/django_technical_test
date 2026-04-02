from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

User = get_user_model()


def htmx_redirect(url):
    response = HttpResponse()
    response["HX-Redirect"] = url
    return response


class LoginPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/dashboard/")
        return render(request, "accounts/login.html")

    def post(self, request):
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return htmx_redirect(request.GET.get("next", "/dashboard/"))
        return render(request, "accounts/partials/form_error.html", {
            "error": "Invalid email or password."
        })


class RegisterPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/dashboard/")
        return render(request, "accounts/register.html")

    def post(self, request):
        email = request.POST.get("email", "").strip()
        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "")
        is_organizer = request.POST.get("is_organizer") == "true"

        if User.objects.filter(email=email).exists():
            return render(request, "accounts/partials/form_error.html", {
                "error": "An account with this email already exists."
            })
        if len(password) < 8:
            return render(request, "accounts/partials/form_error.html", {
                "error": "Password must be at least 8 characters."
            })

        user = User.objects.create_user(email=email, name=name, password=password, is_organizer=is_organizer)
        login(request, user)
        return htmx_redirect("/dashboard/")


class LogoutPageView(View):
    def post(self, request):
        logout(request)
        return redirect("/auth/login/")


class DashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/auth/login/?next=/dashboard/")
        return render(request, "dashboard/index.html")
