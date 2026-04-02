
"""Add total column to archived_orders

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0006'
down_revision: Union[str, Sequence[str], None] = '0005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Способ 1: добавить без NOT NULL (мгновенно)
    op.add_column('archived_orders', 
        sa.Column('total', sa.Numeric(10, 2), nullable=True))
    
    # Способ 2: заполнить существующие строки (если есть данные)
    op.execute("UPDATE archived_orders SET total = 0 WHERE total IS NULL")
    
    # Способ 3: добавить DEFAULT и NOT NULL (теперь быстро, т.к. все строки уже заполнены)
    op.execute("ALTER TABLE archived_orders ALTER COLUMN total SET DEFAULT 0")
    op.alter_column('archived_orders', 'total', nullable=False)

def downgrade() -> None:
    op.drop_column('archived_orders', 'total')