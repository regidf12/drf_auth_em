from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permissions import HasAccess
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden

ARTICLES = [
    {"id": 1, "title": "Hello RBAC", "author": "system"},
    {"id": 2, "title": "Custom JWT done right", "author": "system"},
]


class ArticleListView(APIView):
    permission_classes = [HasAccess]
    access_resource = "articles"
    access_action = "read"

    def get(self, request):
        return Response(ARTICLES)


class ArticleCreateView(APIView):
    permission_classes = [HasAccess]
    access_resource = "articles"
    access_action = "write"

    def post(self, request):
        new_id = max([a["id"] for a in ARTICLES] + [0]) + 1
        title = request.data.get("title", "Untitled")
        article = {"id": new_id, "title": title, "author": str(request.user.email)}
        ARTICLES.append(article)
        return Response(article, status=201)


@login_required
def user_data_view(request):
    if not request.user.has_perm('auth_app.view_userdata'):
        return render(request, "auth/403.html")

    return JsonResponse({
        "username": request.user.username,
        "email": request.user.email
    })


@login_required
def edit_resource_view(request):
    if not request.user.has_perm('auth_app.change_resource'):
        return render(request, "auth/403.html")

    return JsonResponse({
        "status": "ok",
        "message": "Вы успешно изменили ресурс"
    })


@login_required
def admin_only_view(request):
    if not request.user.is_staff:
        return render(request, "auth/403.html")

    return JsonResponse({
        "status": "ok",
        "message": "Добро пожаловать, админ!"
    })
