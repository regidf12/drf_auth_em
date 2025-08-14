from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permissions import HasAccess

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
