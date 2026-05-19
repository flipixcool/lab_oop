"""Добавляю по шаблону из прошлых миграций новый столбец с актвиностью пользователя)

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0007'
down_revision: Union[str, Sequence[str], None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('customers',
        sa.Column('is_active', sa.Boolean(), nullable=True))
    op.execute("UPDATE customers SET is_active = TRUE WHERE is_active IS NULL")
    op.alter_column('customers', 'is_active', nullable=False)


def downgrade() -> None:
    op.drop_column('customers', 'is_active')
