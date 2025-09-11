from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import RegisterForm, EmailAuthenticationForm
from .models import User

def register_view(request):
    if request.user.is_authenticated:
        return redirect("landing")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Регистрация успешна! Войдите, используя свой e-mail и пароль.")
            return redirect("accounts:login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("landing")

    if request.method == "POST":
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # AuthenticationForm сам валидирует
            login(request, user)
            messages.success(request, "Вы вошли в аккаунт.")
            next_url = request.GET.get("next") or reverse("landing")
            return redirect(next_url)
    else:
        form = EmailAuthenticationForm(request)

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Вы вышли из аккаунта.")
    return redirect("landing")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user_obj": request.user})


@login_required
def profile_edit_view(request):
    if request.method == "POST":
        user: User = request.user
        user.first_name = request.POST.get("first_name", "")
        user.middle_name = request.POST.get("middle_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.bio = request.POST.get("bio", "")
        if "avatar" in request.FILES:
            user.avatar = request.FILES["avatar"]
        user.save()
        messages.success(request, "Профиль обновлён.")
        return redirect("accounts:profile")

    return render(request, "accounts/profile_edit.html", {"user_obj": request.user})