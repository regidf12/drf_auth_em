from django.urls import path
from .views import MOCListView, MOCCreateView, MOCListTemplateView, MOCaddListTemplateView

urlpatterns = [
    path("articles", MOCListView.as_view()),
    path("articles/create", MOCCreateView.as_view()),
    path("moc/", MOCListTemplateView.as_view()),
    path("moc_add/", MOCaddListTemplateView.as_view()),
]
