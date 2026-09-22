# SPDX-FileCopyrightText: 2026 ГБПОУ КСТ
#
# SPDX-License-Identifier: MPL-2.0

"""added groups

Revision ID: a680fa3e11df
Revises: 2a95fea0c125
Create Date: 2026-09-22 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
import ormar

# revision identifiers, used by Alembic.
revision = "a680fa3e11df"
down_revision = "2a95fea0c125"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "groups",
        sa.Column("id", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("teacher", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["teacher"], ["users.id"], name="fk_groups_users_id_teacher", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "group_members",
        sa.Column("id", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=False),
        sa.Column("group", ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.ForeignKeyConstraint(["group"], ["groups.id"], name="fk_group_members_groups_id_group", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("group_members")
    op.drop_table("groups")
