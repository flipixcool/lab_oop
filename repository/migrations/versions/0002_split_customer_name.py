"""Split customer name into first_name and last_name

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('customers', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('customers', sa.Column('last_name', sa.String(), nullable=True))

    op.execute("""
        UPDATE customers
        SET first_name = split_part(name, ' ', 1),
            last_name  = NULLIF(split_part(name, ' ', 2), '')
    """)

    op.alter_column('customers', 'first_name', nullable=False)
    op.alter_column('customers', 'last_name', nullable=False)
    op.drop_column('customers', 'name')


def downgrade() -> None:
    op.add_column('customers', sa.Column('name', sa.String(), nullable=True))
    op.execute("UPDATE customers SET name = first_name || ' ' || last_name")
    op.alter_column('customers', 'name', nullable=False)
    op.drop_column('customers', 'last_name')
    op.drop_column('customers', 'first_name')
