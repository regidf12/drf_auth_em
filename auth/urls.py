from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('admin/', include('accounts.admin_urls')),
    path('sor/', include('source.urls')),
]
