from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('admin/', include('accounts.admin_urls')),
    path('sor/', include('source.urls')),
    path('', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('profile/', views.profile_view, name="profile"),
    path('update/', views.update_profile_view, name="update_profile"),
    path('delete/', views.delete_account_view, name="delete_account"),

]
