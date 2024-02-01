from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.generic import View

from .forms import LoginForm, RegisterForm


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, "users/login.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect("home")

            form.add_error(None, "Invalid email or password")

        return render(request, "users/login.html", {"form": form})


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password")

            user.set_password(password)
            user.save()

            return redirect("login")

        return render(request, "users/register.html", {"form": form})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")
