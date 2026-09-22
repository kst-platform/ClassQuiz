# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
# SPDX-FileCopyrightText: 2026 ГБПОУ КСТ
#
# SPDX-License-Identifier: MPL-2.0

"""Управление учётками преподавателей для КСТ.Квиз.

Всё здесь защищено get_admin_user (settings.admins, см. classquiz/auth.py) —
доступ есть только у учёток, явно перечисленных в переменной окружения
ADMINS, а не у "первой строки в базе", как было в апстриме.

Любое действие, которое стирает данные другого человека без права отмены
(удаление учётки), требует повторного ввода **своего собственного** пароля
администратора в теле запроса — тот же паттерн, что уже используется в
апстриме для самостоятельного удаления аккаунта (DELETE /api/v1/users/me).
Так исключается сценарий "кто-то получил доступ к открытой сессии в браузере
администратора и нажал одну кнопку".
"""

import uuid
from datetime import datetime
from uuid import UUID

from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from classquiz.auth import get_admin_user, get_password_hash, verify_password
from classquiz.cache import clear_cache_for_account
from classquiz.db.models import User, UserSession
from classquiz.helpers.avatar import gzipped_user_avatar

router = APIRouter()

_LIST_EXCLUDE = {
    "password",
    "verify_key",
    "usersessions",
    "avatar",
    "quizs",
    "fidocredentialss",
    "backup_code",
    "apikeys",
    "totp_secret",
}


async def _require_admin_password(admin: User, admin_password: str) -> None:
    if not verify_password(admin_password, admin.password):
        raise HTTPException(status_code=403, detail="Неверный пароль администратора")


async def _sign_out_everywhere(user: User) -> None:
    await UserSession.objects.filter(user=user).delete()
    await clear_cache_for_account(user)


@router.get("/users", response_model=list[User], response_model_exclude=_LIST_EXCLUDE)
async def list_users(_: User = Depends(get_admin_user)):
    return await User.objects.order_by(User.created_at.asc()).all()


@router.get("/users/pending", response_model=list[User], response_model_exclude=_LIST_EXCLUDE)
async def list_pending_users(_: User = Depends(get_admin_user)):
    """Учётки, которые сами зарегистрировались и ждут одобрения."""
    return await User.objects.filter(approved=False).order_by(User.created_at.asc()).all()


@router.post("/users/{user_id}/approve")
async def approve_user(user_id: UUID, _: User = Depends(get_admin_user)):
    user = await User.objects.get_or_none(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Учётка не найдена")
    user.approved = True
    await user.update()
    return {"message": "Учётка одобрена"}


class CreateUserInput(BaseModel):
    email: str
    username: str
    password: str


@router.post("/users", response_model=User, response_model_exclude=_LIST_EXCLUDE)
async def create_user_as_admin(data: CreateUserInput, _: User = Depends(get_admin_user)):
    """Админ создаёт учётку сам — сразу approved, без очереди одобрения."""
    try:
        validate_email(data.email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    existing = await User.objects.filter((User.email == data.email) | (User.username == data.username)).all()
    if len(existing) != 0:
        raise HTTPException(status_code=409, detail="Учётка с такой почтой или именем уже существует")
    user = User(
        id=uuid.uuid4(),
        email=data.email,
        username=data.username,
        password=get_password_hash(data.password),
        avatar=gzipped_user_avatar(),
        created_at=datetime.now(),
        verified=True,
        approved=True,
    )
    await user.save()
    return user


class ResetPasswordInput(BaseModel):
    new_password: str
    admin_password: str


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(user_id: UUID, data: ResetPasswordInput, admin: User = Depends(get_admin_user)):
    await _require_admin_password(admin, data.admin_password)
    user = await User.objects.get_or_none(id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Учётка не найдена")
    user.password = get_password_hash(data.new_password)
    await user.update()
    # Старые сессии и токены становятся бесполезны — это как раз то, что
    # должно произойти, если пароль меняет не сам владелец учётки.
    await _sign_out_everywhere(user)
    return {"message": "Пароль обновлён"}


class DeleteUserByIdInput(BaseModel):
    user_id: UUID
    admin_password: str


@router.delete("/user/id")
async def delete_user_by_id(data: DeleteUserByIdInput, admin: User = Depends(get_admin_user)):
    await _require_admin_password(admin, data.admin_password)
    return {"deleted": await User.objects.delete(id=data.user_id)}


class DeleteUserByUsernameInput(BaseModel):
    username: str
    admin_password: str


@router.delete("/user/username")
async def delete_user_by_username(data: DeleteUserByUsernameInput, admin: User = Depends(get_admin_user)):
    await _require_admin_password(admin, data.admin_password)
    return {"deleted": await User.objects.delete(username=data.username)}


class DeleteUserByEmailInput(BaseModel):
    email: str
    admin_password: str


@router.delete("/user/email")
async def delete_user_by_email(data: DeleteUserByEmailInput, admin: User = Depends(get_admin_user)):
    await _require_admin_password(admin, data.admin_password)
    return {"deleted": await User.objects.delete(email=data.email)}
