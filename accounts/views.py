from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import SigninForm

from .models import UserProfile

"""
Function for get sign form
"""


def signin_view(request):
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            user1 = User.objects.create_user(
                username=username, password=password, email=email)
            device = form.cleaned_data["device"]
            UserProfile.objects.create(user=user1, user_device=device)
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect("/")

    else:
        form = SigninForm()
    context = {"form": form}
    return render(request, "accounts/signin.html", context)
