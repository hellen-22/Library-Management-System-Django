from django.shortcuts import render
from django.views.generic import View


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "users/login.html")
