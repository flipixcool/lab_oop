"""Extract categories into a separate table (3NF)

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    op.execute("""
        INSERT INTO categories (name)
        SELECT DISTINCT category FROM products
    """)

    op.add_column('products', sa.Column('category_id', sa.Integer(), nullable=True))

    op.execute("""
        UPDATE products
        SET category_id = categories.id
        FROM categories
        WHERE categories.name = products.category
    """)

    op.alter_column('products', 'category_id', nullable=False)

    op.create_foreign_key(
        'fk_products_category_id',
        'products', 'categories',
        ['category_id'], ['id'],
    )

    op.drop_column('products', 'category')


def downgrade() -> None:
    op.add_column('products', sa.Column('category', sa.String(), nullable=True))

    op.execute("""
        UPDATE products
        SET category = categories.name
        FROM categories
        WHERE categories.id = products.category_id
    """)

    op.alter_column('products', 'category', nullable=False)

    op.drop_constraint('fk_products_category_id', 'products', type_='foreignkey')
    op.drop_column('products', 'category_id')
    op.drop_table('categories')
