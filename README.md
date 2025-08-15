# DRF AuthN/AuthZ

**Стек:** Django REST Framework + Postgres, PyJWT.

## Быстрый старт

```bash
python -m venv venv 
.venv/bin/activate
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Схема БД

- **accounts_user** — кастомный пользователь (email-логин, soft-delete).
    - `id` (UUID), `email` (unique), `first_name`, `last_name`, `patronymic` (
      nullable), `is_active`, `is_staff`, `is_superuser`,
    - `token_version` (int) — инкремент для глобального logout,
    - `deleted_at` (nullable).
- **accounts_role** — роли (например, admin, editor, viewer).
- **accounts_permission** — разрешение = (`resource`, `action`, `effect`)
- **accounts_rolepermission** — M2M: роль - разрешение.
- **accounts_userrole** — M2M: пользователь - роль.
- **accounts_refreshtoken** — активные refresh-токены (rotation), `jti`, `expires_at`, `is_revoked`.
- **accounts_blacklistedtoken** — список отозванных access-токенов по `jti` (живут до истечения access-токена).

### Модель доступа

- Request маппится на пару (**resource**, **action**). Пример: `("articles", "read")`, `("articles", "write")`.
- Пользователь **имеет доступ**, если **хотя бы одно** правило из объединения его ролей дает `ALLOW`:
    - Точное совпадение ресурса и действия, либо совпадение по wildcard: ресурс `*` или действие `*`.
    - DENY (если бы использовали, переопределяет allow; в демо мы создаем только ALLOW).
- Если пользователь не аутентифицирован → 401. Аутентифицирован, но не имеет доступа → 403.

## JWT

- `access` (по умолчанию 15 минут) — короткоживущий, только в заголовке `Authorization: Bearer <token>`.
- `refresh` (30 дней) — хранится на клиенте, ротируется; запись в БД (таблица `RefreshToken`) + флаг `is_revoked`.

- **Logout**: одиночная сессия — revoke refresh (и текущий access добавляем в blacklist до его exp).  
  **Logout all** — инкремент `token_version` у пользователя и revoke всех refresh'ей.

## Эндпоинты

Аутентификация:

- `POST /auth/register` — регистрация.
- `POST /auth/login` — логин по email/паролю, выдает access/refresh.
- `POST /auth/refresh` — обновить пару токенов (rotation).
- `POST /auth/logout` — выход из текущей сессии.
- `POST /auth/logout_all` — завершить все сессии.
- `GET /me` — профиль (нужен access).
- `PUT/PATCH /me` — обновление профиля.
- `DELETE /me` — мягкое удаление (is_active=False).

Админка ACL (только для роли `admin`):

- `GET/POST /admin/roles`
- `GET/POST /admin/permissions`
- `POST /admin/roles/{role_id}/attach_permission/{perm_id}`
- `POST /admin/users/{user_id}/attach_role/{role_id}`

Бизнес-ресурсы (mock):

- `GET /resources/articles` — нужна permission `("articles", "read")`
- `POST /resources/articles` — нужна `("articles", "write")`
