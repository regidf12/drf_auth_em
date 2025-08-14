from rest_framework.permissions import BasePermission
from .models import UserRole, RolePermission, Permission


class HasAccess(BasePermission):
    message = "Forbidden"

    def has_permission(self, request, view):
        resource = getattr(view, "access_resource", None)
        action = getattr(view, "access_action", None)
        if not resource or not action:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        role_ids = list(UserRole.objects.filter(user=user).values_list("role_id", flat=True))
        if not role_ids and not user.is_superuser:
            return False

        if user.is_superuser:
            return True

        perms = RolePermission.objects.filter(role_id__in=role_ids).select_related("permission")
        allow = False
        for rp in perms:
            p = rp.permission
            res_ok = (p.resource == resource) or (p.resource == "*")
            act_ok = (p.action == action) or (p.action == "*")
            if res_ok and act_ok:
                if p.effect == Permission.DENY:
                    self.message = "Explicitly denied"
                    return False
                allow = True
        return allow
