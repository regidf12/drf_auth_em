from django.urls import path
from .views import RoleListCreateView, PermissionListCreateView, AttachPermissionToRoleView, AttachRoleToUserView

urlpatterns = [
    path("roles", RoleListCreateView.as_view()),
    path("permissions", PermissionListCreateView.as_view()),
    path("roles/<int:role_id>/attach_permission/<int:perm_id>", AttachPermissionToRoleView.as_view()),
    path("users/<uuid:user_id>/attach_role/<int:role_id>", AttachRoleToUserView.as_view()),
]
