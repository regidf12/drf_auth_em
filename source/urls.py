from django.urls import path
from .views import ArticleListView, ArticleCreateView, user_data_view, edit_resource_view, admin_only_view

urlpatterns = [
    path("articles", ArticleListView.as_view()),
    path("articles/create", ArticleCreateView.as_view()),
    path('resource/user-data/', user_data_view, name='user_data'),
    path('resource/edit/', edit_resource_view, name='edit_resource'),
    path('resource/admin/', admin_only_view, name='admin_only'),
]
