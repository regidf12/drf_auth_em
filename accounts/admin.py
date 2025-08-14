from django.contrib import admin
from .models import User, Role, Permission, RolePermission, UserRole, RefreshToken, BlacklistedToken
from django.contrib.auth.models import Group


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_active", "is_staff", "token_version")
    search_fields = ("email", "first_name", "last_name")


admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)
admin.site.register(UserRole)
admin.site.register(RefreshToken)
admin.site.register(BlacklistedToken)
admin.site.unregister(Group)
