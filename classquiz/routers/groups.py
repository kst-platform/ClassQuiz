# SPDX-FileCopyrightText: 2026 ГБПОУ КСТ
#
# SPDX-License-Identifier: MPL-2.0

"""Группы студентов для КСТ.Квиз.

У студентов нет своих учёток — группа это просто список ФИО, которым
преподаватель владеет и может привязать к игровой сессии (см.
classquiz/routers/quiz.py start_quiz и join_game в classquiz/socket_server).
Каждый эндпоинт проверяет, что группа принадлежит текущему пользователю —
чужую группу нельзя ни посмотреть, ни изменить, ни привязать к своей игре.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from classquiz.auth import get_current_user
from classquiz.db.models import Group, GroupMember, User

router = APIRouter()


class GroupOut(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    member_count: int


class GroupMemberOut(BaseModel):
    id: uuid.UUID
    full_name: str


class GroupDetailOut(GroupOut):
    members: list[GroupMemberOut]


async def _get_own_group_or_404(group_id: uuid.UUID, user: User) -> Group:
    group = await Group.objects.get_or_none(id=group_id, teacher=user)
    if group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return group


@router.get("", response_model=list[GroupOut])
async def list_groups(user: User = Depends(get_current_user)):
    groups = await Group.objects.filter(teacher=user).order_by(Group.created_at.asc()).all()
    out = []
    for g in groups:
        count = await GroupMember.objects.filter(group=g).count()
        out.append(GroupOut(id=g.id, name=g.name, created_at=g.created_at, member_count=count))
    return out


class CreateGroupInput(BaseModel):
    name: str


@router.post("", response_model=GroupOut)
async def create_group(data: CreateGroupInput, user: User = Depends(get_current_user)):
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Название группы не может быть пустым")
    group = await Group.objects.create(id=uuid.uuid4(), name=name, teacher=user, created_at=datetime.now())
    return GroupOut(id=group.id, name=group.name, created_at=group.created_at, member_count=0)


@router.get("/{group_id}", response_model=GroupDetailOut)
async def get_group(group_id: uuid.UUID, user: User = Depends(get_current_user)):
    group = await _get_own_group_or_404(group_id, user)
    members = await GroupMember.objects.filter(group=group).order_by(GroupMember.full_name.asc()).all()
    return GroupDetailOut(
        id=group.id,
        name=group.name,
        created_at=group.created_at,
        member_count=len(members),
        members=[GroupMemberOut(id=m.id, full_name=m.full_name) for m in members],
    )


class RenameGroupInput(BaseModel):
    name: str


@router.patch("/{group_id}", response_model=GroupOut)
async def rename_group(group_id: uuid.UUID, data: RenameGroupInput, user: User = Depends(get_current_user)):
    group = await _get_own_group_or_404(group_id, user)
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Название группы не может быть пустым")
    group.name = name
    await group.update()
    count = await GroupMember.objects.filter(group=group).count()
    return GroupOut(id=group.id, name=group.name, created_at=group.created_at, member_count=count)


@router.delete("/{group_id}")
async def delete_group(group_id: uuid.UUID, user: User = Depends(get_current_user)):
    group = await _get_own_group_or_404(group_id, user)
    await group.delete()
    return {"message": "Группа удалена"}


class AddMembersInput(BaseModel):
    # Одно ФИО на строку — вставка списка из журнала/таблицы одним куском,
    # без отдельного запроса на каждого студента.
    names: str


@router.post("/{group_id}/members", response_model=GroupDetailOut)
async def add_members(group_id: uuid.UUID, data: AddMembersInput, user: User = Depends(get_current_user)):
    group = await _get_own_group_or_404(group_id, user)
    existing = {m.full_name for m in await GroupMember.objects.filter(group=group).all()}
    added = 0
    for line in data.names.splitlines():
        full_name = line.strip()
        if not full_name or full_name in existing:
            continue
        await GroupMember.objects.create(id=uuid.uuid4(), group=group, full_name=full_name)
        existing.add(full_name)
        added += 1
    members = await GroupMember.objects.filter(group=group).order_by(GroupMember.full_name.asc()).all()
    return GroupDetailOut(
        id=group.id,
        name=group.name,
        created_at=group.created_at,
        member_count=len(members),
        members=[GroupMemberOut(id=m.id, full_name=m.full_name) for m in members],
    )


@router.delete("/{group_id}/members/{member_id}")
async def remove_member(group_id: uuid.UUID, member_id: uuid.UUID, user: User = Depends(get_current_user)):
    group = await _get_own_group_or_404(group_id, user)
    member = await GroupMember.objects.get_or_none(id=member_id, group=group)
    if member is None:
        raise HTTPException(status_code=404, detail="Студент не найден в этой группе")
    await member.delete()
    return {"message": "Удалено"}
