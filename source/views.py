from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permissions import HasAccess
from django.shortcuts import render
from django.views.generic import TemplateView

ARTICLES = [
    {"id": 1, "title": "Hello world!", "author": "system"},
    {"id": 2, "title": "Think differently", "author": "system"},
]


@method_decorator(login_required, name='dispatch')
class MOCListView(APIView):
    permission_classes = [HasAccess]
    access_resource = "articles"
    access_action = "read"

    def get(self, request):
        return Response(ARTICLES)


@method_decorator(login_required, name='dispatch')
class MOCCreateView(APIView):
    permission_classes = [HasAccess]
    access_resource = "articles"
    access_action = "write"

    def post(self, request):
        new_id = max([a["id"] for a in ARTICLES] + [0]) + 1
        title = request.data.get("title", "Untitled")
        article = {
            "id": new_id,
            "title": title,
            "author": str(request.user.email)
        }
        ARTICLES.append(article)
        return Response(article, status=201)


class MOCListTemplateView(TemplateView):
    template_name = "auth/mocs.html"
    permission_classes = [HasAccess]
    access_resource = "articles"
    access_action = "read"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = ARTICLES
        return context


class MOCaddListTemplateView(TemplateView):
    template_name = "auth/mocs_add.html"

    def post(self, request):
        title = request.data.get("title", "Untitled")
        new_id = max([a["id"] for a in ARTICLES] + [0]) + 1
        article = {
            "id": new_id,
            "title": title,
            "author": str(request.user.email) if request.user.is_authenticated else "anonymous"
        }
        ARTICLES.append(article)
