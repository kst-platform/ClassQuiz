# SPDX-FileCopyrightText: 2026 ГБПОУ КСТ
#
# SPDX-License-Identifier: MPL-2.0

"""added admin approval field

Revision ID: 2a95fea0c125
Revises: 9d7fa2e6b24c
Create Date: 2026-09-22 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "2a95fea0c125"
down_revision = "9d7fa2e6b24c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # По умолчанию False у уже существующих строк (fail closed) — учётки,
    # созданные до этой миграции, тоже должны пройти через одобрение админа,
    # а не получить доступ автоматически.
    op.add_column(
        "users",
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "approved")
