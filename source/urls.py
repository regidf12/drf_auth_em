from django.urls import path
from source.views import ArticleListView, ArticleCreateView

urlpatterns = [
    path("articles", ArticleListView.as_view()),
    path("articles/create", ArticleCreateView.as_view()),
]
