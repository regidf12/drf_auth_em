from django.urls import path
from .views import RegisterView, LoginView, MeView, RefreshView, LogoutView, LogoutAllView

urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("refresh", RefreshView.as_view()),
    path("logout", LogoutView.as_view()),
    path("logout_all", LogoutAllView.as_view()),
    path("me", MeView.as_view()),
]
