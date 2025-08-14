import jwt
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, RoleSerializer, PermissionSerializer, \
    RolePermissionSerializer, UserRoleSerializer, RefreshSerializer
from .auth import mint_access_token, mint_refresh_token, decode_token, blacklist_access, revoke_all_refresh, \
    revoke_refresh_by_jti
from .models import User, Role, Permission, RolePermission, UserRole, RefreshToken
from .permissions import HasAccess


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        user = ser.validated_data["user"]
        access, access_payload = mint_access_token(user)
        refresh, refresh_payload, rt = mint_refresh_token(user)
        return Response({
            "access": access,
            "refresh": refresh,
            "user": UserSerializer(user).data
        })


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        ser = UserSerializer(instance=request.user, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    def patch(self, request):
        ser = UserSerializer(instance=request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    def delete(self, request):
        user = request.user
        user.soft_delete()
        revoke_all_refresh(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = RefreshSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data["refresh"]
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return Response({"detail": "Invalid token type"}, status=400)
        try:
            rt = RefreshToken.objects.get(jti=payload["jti"])
        except RefreshToken.DoesNotExist:
            return Response({"detail": "Unknown refresh token"}, status=401)
        if rt.is_revoked or rt.expires_at <= timezone.now():
            return Response({"detail": "Refresh revoked or expired"}, status=401)
        with transaction.atomic():
            rt.is_revoked = True
            rt.save(update_fields=["is_revoked"])
            user = rt.user
            if not user.is_active or user.token_version != payload.get("tv"):
                return Response({"detail": "User inactive or invalidated"}, status=401)
            access, _ = mint_access_token(user)
            refresh, refresh_payload, _ = mint_refresh_token(user)
        return Response({"access": access, "refresh": refresh})


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                payload = decode_token(refresh_token)
                if payload.get("type") == "refresh":
                    revoke_refresh_by_jti(payload.get("jti"))
            except Exception:
                pass
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Bearer "):
            try:
                access_payload = jwt.decode(auth.split(" ", 1)[1], settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
                blacklist_access(access_payload.get("jti"), access_payload.get("exp"))
            except Exception:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutAllView(APIView):
    def post(self, request):
        user = request.user
        user.token_version += 1
        user.save(update_fields=["token_version"])
        revoke_all_refresh(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [HasAccess]
    access_resource = "acl.roles"
    access_action = "write"


class PermissionListCreateView(generics.ListCreateAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [HasAccess]
    access_resource = "acl.permissions"
    access_action = "write"


class AttachPermissionToRoleView(APIView):
    permission_classes = [HasAccess]
    access_resource = "acl.roles"
    access_action = "write"

    def post(self, request, role_id, perm_id):
        role = Role.objects.get(id=role_id)
        perm = Permission.objects.get(id=perm_id)
        RolePermission.objects.get_or_create(role=role, permission=perm)
        return Response({"detail": "attached"})


class AttachRoleToUserView(APIView):
    permission_classes = [HasAccess]
    access_resource = "acl.users"
    access_action = "write"

    def post(self, request, user_id, role_id):
        user = User.objects.get(id=user_id)
        role = Role.objects.get(id=role_id)
        UserRole.objects.get_or_create(user=user, role=role)
        return Response({"detail": "attached"})
