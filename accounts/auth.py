import uuid, jwt, datetime
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from .models import User, RefreshToken, BlacklistedToken


def _now():
    return timezone.now()


def _exp(minutes=15):
    return _now() + datetime.timedelta(minutes=minutes)


def _exp_days(days=30):
    return _now() + datetime.timedelta(days=days)


def mint_access_token(user, jti=None):
    if jti is None:
        jti = uuid.uuid4()
    payload = {
        "sub": str(user.id),
        "type": "access",
        "jti": str(jti),
        "iat": int(_now().timestamp()),
        "exp": int(_exp(settings.JWT_ACCESS_TTL_MIN).timestamp()),
        "tv": user.token_version,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token, payload


def mint_refresh_token(user):
    jti = uuid.uuid4()
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": str(jti),
        "iat": int(_now().timestamp()),
        "exp": int(_exp_days(settings.JWT_REFRESH_TTL_DAYS).timestamp()),
        "tv": user.token_version,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    rt = RefreshToken.objects.create(
        user=user,
        jti=jti,
        expires_at=datetime.datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc),
    )
    return token, payload, rt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        return payload
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed("Token expired")
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed("Invalid token")


class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed("Invalid Authorization header")
        token = auth[1].decode("utf-8")

        payload = decode_token(token)
        if payload.get("type") != "access":
            raise exceptions.AuthenticationFailed("Invalid token type")
        jti = payload.get("jti")
        if BlacklistedToken.objects.filter(jti=jti).exists():
            raise exceptions.AuthenticationFailed("Token revoked")
        user_id = payload.get("sub")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")
        if not user.is_active or user.token_version != payload.get("tv"):
            raise exceptions.AuthenticationFailed("Inactive or invalidated token")
        return (user, payload)


def blacklist_access(jti: str, exp_ts: int):
    expires_at = datetime.datetime.fromtimestamp(exp_ts, tz=datetime.timezone.utc)
    try:
        BlacklistedToken.objects.get_or_create(jti=jti, defaults={"expires_at": expires_at})
    except Exception:
        pass


def revoke_all_refresh(user):
    RefreshToken.objects.filter(user=user, is_revoked=False).update(is_revoked=True)


def revoke_refresh_by_jti(jti: str):
    RefreshToken.objects.filter(jti=jti).update(is_revoked=True)
