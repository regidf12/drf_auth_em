from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from accounts.models import User


@csrf_protect
def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        patronymic = request.POST.get("patronymic")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Пароли не совпадают")
            return render(request, "auth/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email уже зарегистрирован")
            return render(request, "auth/register.html")

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            password=password
        )
        messages.success(request, "Регистрация успешна! Теперь войдите.")
        return redirect("login")

    return render(request, "auth/register.html")


@csrf_protect
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect("profile")
        else:
            messages.error(request, "Неверные учетные данные или аккаунт неактивен.")
    return render(request, "auth/login.html")


@login_required
def profile_view(request):
    return render(request, "auth/profile.html", {"user": request.user})


@login_required
@csrf_protect
def update_profile_view(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.patronymic = request.POST.get("patronymic")
        request.user.email = request.POST.get("email")
        request.user.save()
        messages.success(request, "Данные обновлены")
        return redirect("profile")
    return render(request, "auth/update.html", {"user": request.user})


@login_required
@csrf_protect
def delete_account_view(request):
    if request.method == "POST":
        request.user.is_active = False
        request.user.save()
        logout(request)
        messages.success(request, "Аккаунт удалён (деактивирован)")
        return redirect("login")
    return render(request, "auth/delete.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def error_401_view(request, exception=None):
    return render(request, "error/401.html", status=401)


def error_403_view(request, exception=None):
    return render(request, "error/403.html", status=403)
