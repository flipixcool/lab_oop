import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from repository.models_orm import (
    CustomerORM, CategoryORM, ProductORM,
    OrderORM, OrderItemORM, WarehouseORM, ArchivedOrderORM,
)
from domain.model import LoyaltyLevel, OrderStatus


# ── CustomerORM ───────────────────────────────────────────────────────────────

class TestCustomerORM:
    def test_fields_assigned(self):
        orm = CustomerORM(
            first_name="Иван",
            last_name="Иванов",
            email="ivan@mail.ru",
            loyalty_level=LoyaltyLevel.BRONZE.value,
        )
        assert orm.first_name == "Иван"
        assert orm.last_name == "Иванов"
        assert orm.email == "ivan@mail.ru"
        assert orm.loyalty_level == "bronze"

    def test_tablename(self):
        assert CustomerORM.__tablename__ == "customers"

    def test_loyalty_level_values(self):
        for level in LoyaltyLevel:
            orm = CustomerORM(
                first_name="А", last_name="Б", email="a@b.com",
                loyalty_level=level.value,
            )
            assert orm.loyalty_level == level.value


# ── CategoryORM ───────────────────────────────────────────────────────────────

class TestCategoryORM:
    def test_fields_assigned(self):
        cat = CategoryORM(name="Электроника")
        assert cat.name == "Электроника"

    def test_tablename(self):
        assert CategoryORM.__tablename__ == "categories"


# ── ProductORM ────────────────────────────────────────────────────────────────

class TestProductORM:
    def test_fields_assigned(self):
        orm = ProductORM(name="Ноутбук", price=50000.0, category_id=1, is_active=True)
        assert orm.name == "Ноутбук"
        assert orm.price == 50000.0
        assert orm.category_id == 1
        assert orm.is_active is True

    def test_tablename(self):
        assert ProductORM.__tablename__ == "products"

    def test_explicit_is_active_false(self):
        orm = ProductORM(name="Мышь", price=500.0, category_id=2, is_active=False)
        assert orm.is_active is False


# ── WarehouseORM ──────────────────────────────────────────────────────────────

class TestWarehouseORM:
    def test_fields_assigned(self):
        orm = WarehouseORM(product_id=1, quantity=42)
        assert orm.product_id == 1
        assert orm.quantity == 42

    def test_tablename(self):
        assert WarehouseORM.__tablename__ == "warehouse"

    def test_zero_quantity(self):
        orm = WarehouseORM(product_id=5, quantity=0)
        assert orm.quantity == 0


# ── ArchivedOrderORM ──────────────────────────────────────────────────────────

class TestArchivedOrderORM:
    def test_fields_assigned(self):
        now = datetime.now()
        orm = ArchivedOrderORM(
            id=1,
            customer_id=2,
            status="delivered",
            discount=10.0,
            total=4500.0,
            created_at=now,
            archived_at=now,
        )
        assert orm.id == 1
        assert orm.customer_id == 2
        assert orm.status == "delivered"
        assert orm.discount == 10.0
        assert orm.total == 4500.0
        assert orm.created_at == now
        assert orm.archived_at == now

    def test_tablename(self):
        assert ArchivedOrderORM.__tablename__ == "archived_orders"

    def test_zero_discount(self):
        now = datetime.now()
        orm = ArchivedOrderORM(
            id=1, customer_id=1, status="cancelled",
            discount=0.0, total=0.0, created_at=now, archived_at=now,
        )
        assert orm.discount == 0.0


# ── OrderItemORM ──────────────────────────────────────────────────────────────

class TestOrderItemORM:
    def test_fields_assigned(self):
        orm = OrderItemORM(order_id=1, product_id=2, quantity=3, unit_price=999.0)
        assert orm.order_id == 1
        assert orm.product_id == 2
        assert orm.quantity == 3
        assert orm.unit_price == 999.0

    def test_tablename(self):
        assert OrderItemORM.__tablename__ == "order_items"
