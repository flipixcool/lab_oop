import pytest
from domain.model import Customer, Product, OrderItem, Order, Warehouse, LoyaltyLevel, OrderStatus
from domain.exceptions import ValidationError, InsufficientStockError


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def customer():
    c = Customer("Иван", "ivan@mail.ru", "bronze")
    c.id = 1
    return c

@pytest.fixture
def product():
    p = Product("Пицца", 500, "Еда")
    p.id = 1
    return p

@pytest.fixture
def order_item(product):
    return OrderItem(product, 2)

@pytest.fixture
def order(customer, order_item):
    return Order(customer.id, [order_item])


# ── Customer ──────────────────────────────────────────────────────────────────

class TestCustomer:
    def test_create_valid(self, customer):
        assert customer.name == "Иван"
        assert customer.email == "ivan@mail.ru"
        assert customer.loyalty_level == LoyaltyLevel.BRONZE

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            Customer("", "ivan@mail.ru")

    def test_empty_email_raises(self):
        with pytest.raises(ValidationError):
            Customer("Иван", "")

    def test_invalid_loyalty_level_raises(self):
        with pytest.raises(ValueError):
            Customer("Иван", "ivan@mail.ru", "vip")

    def test_loyalty_level_setter(self, customer):
        customer.loyalty_level = "gold"
        assert customer.loyalty_level == LoyaltyLevel.GOLD

    def test_loyalty_level_setter_invalid_raises(self, customer):
        with pytest.raises(ValueError):
            customer.loyalty_level = "vip"

    def test_upgrade_bronze_to_silver(self, customer):
        customer.upgrade()
        assert customer.loyalty_level == LoyaltyLevel.SILVER

    def test_upgrade_silver_to_gold(self, customer):
        customer.loyalty_level = "silver"
        customer.upgrade()
        assert customer.loyalty_level == LoyaltyLevel.GOLD

    def test_upgrade_gold_stays_gold(self, customer):
        customer.loyalty_level = "gold"
        customer.upgrade()
        assert customer.loyalty_level == LoyaltyLevel.GOLD

    def test_activate(self, customer):
        customer.loyalty_level = "silver"
        customer.activate()
        assert customer.loyalty_level == LoyaltyLevel.BRONZE

    def test_close(self, customer):
        customer.close()
        assert customer.loyalty_level == LoyaltyLevel.BRONZE

    def test_eq_same_id(self, customer):
        assert customer == customer

    def test_eq_different_customers(self, customer):
        other = Customer("Мария", "maria@mail.ru")
        other.id = 2
        assert customer != other

    def test_str(self, customer):
        assert "Иван" in str(customer)
        assert "ivan@mail.ru" in str(customer)

    def test_repr(self, customer):
        assert "Customer(" in repr(customer)
        assert "Иван" in repr(customer)

    def test_eq_non_customer(self, customer):
        assert customer != "not a customer"
        assert customer != 42


# ── Product ───────────────────────────────────────────────────────────────────

class TestProduct:
    def test_create_valid(self, product):
        assert product.name == "Пицца"
        assert product.price == 500
        assert product.category == "Еда"
        assert product.is_active is True

    def test_zero_price_raises(self):
        with pytest.raises(ValidationError):
            Product("Пицца", 0, "Еда")

    def test_negative_price_raises(self):
        with pytest.raises(ValidationError):
            Product("Пицца", -100, "Еда")

    def test_empty_category_raises(self):
        with pytest.raises(ValidationError):
            Product("Пицца", 500, "")

    def test_price_setter_valid(self, product):
        product.price = 700
        assert product.price == 700

    def test_price_setter_zero_raises(self, product):
        with pytest.raises(ValidationError):
            product.price = 0

    def test_activate_deactivate(self, product):
        product.deactivate()
        assert product.is_active is False
        product.activate()
        assert product.is_active is True

    def test_lt_sorting(self):
        p1 = Product("Дорогой", 1000, "cat")
        p2 = Product("Дешевый", 100, "cat")
        assert p2 < p1
        assert sorted([p1, p2])[0] == p2

    def test_str(self, product):
        assert "Пицца" in str(product)
        assert "500" in str(product)

    def test_repr(self, product):
        assert "Product(" in repr(product)


# ── OrderItem ─────────────────────────────────────────────────────────────────

class TestOrderItem:
    def test_subtotal(self, order_item):
        assert order_item.subtotal == 1000

    def test_unit_price_fixed_on_creation(self, product):
        item = OrderItem(product, 2)
        product.price = 999
        assert item.unit_price == 500
        assert item.subtotal == 1000

    def test_zero_quantity_raises(self, product):
        with pytest.raises(ValidationError):
            OrderItem(product, 0)

    def test_negative_quantity_raises(self, product):
        with pytest.raises(ValidationError):
            OrderItem(product, -1)

    def test_wrong_product_type_raises(self):
        with pytest.raises(ValidationError):
            OrderItem("not a product", 1)

    def test_str(self, order_item):
        assert "Пицца" in str(order_item)
        assert "1000" in str(order_item)


# ── Order ─────────────────────────────────────────────────────────────────────

class TestOrder:
    def test_create_valid(self, order, customer):
        assert order.customer_id == customer.id
        assert order.status == OrderStatus.PENDING
        assert order.discount == 0.0

    def test_total(self, order):
        assert order.total == 1000

    def test_none_customer_id_raises(self, order_item):
        with pytest.raises(ValidationError):
            Order(None, [order_item])

    def test_empty_items_raises(self, customer):
        with pytest.raises(ValidationError):
            Order(customer.id, [])

    def test_negative_discount_raises(self, customer, order_item):
        with pytest.raises(ValidationError):
            Order(customer.id, [order_item], discount=-1)

    def test_discount_over_100_raises(self, customer, order_item):
        with pytest.raises(ValidationError):
            Order(customer.id, [order_item], discount=101)

    def test_change_status(self, order):
        order.change_status("confirmed")
        assert order.status == OrderStatus.CONFIRMED

    def test_change_status_invalid_raises(self, order):
        with pytest.raises(ValueError):
            order.change_status("unknown")

    def test_add_item(self, order, product):
        new_item = OrderItem(product, 1)
        order.add_item(new_item)
        assert len(order.items) == 2
        assert order.total == 1500

    def test_lt_sorting(self, customer, order_item):
        from datetime import datetime, timedelta
        old = Order(customer.id, [order_item], created_at=datetime.now() - timedelta(days=1))
        new = Order(customer.id, [order_item], created_at=datetime.now())
        assert old < new

    def test_str(self, order):
        assert "₽" in str(order)
        assert "pending" in str(order)


# ── Warehouse ─────────────────────────────────────────────────────────────────

class TestWarehouse:
    def test_add_and_get_stock(self):
        w = Warehouse()
        w.add_stock(1, 10)
        assert w.get_stock(1) == 10

    def test_add_stock_accumulates(self):
        w = Warehouse()
        w.add_stock(1, 5)
        w.add_stock(1, 3)
        assert w.get_stock(1) == 8

    def test_get_stock_missing_product(self):
        w = Warehouse()
        assert w.get_stock(99) == 0

    def test_has_enough_true(self):
        w = Warehouse()
        w.add_stock(1, 10)
        assert w.has_enough(1, 5) is True

    def test_has_enough_false(self):
        w = Warehouse()
        w.add_stock(1, 2)
        assert w.has_enough(1, 5) is False

    def test_remove_stock(self):
        w = Warehouse()
        w.add_stock(1, 10)
        w.remove_stock(1, 4, "Пицца")
        assert w.get_stock(1) == 6

    def test_remove_stock_insufficient_raises(self):
        w = Warehouse()
        w.add_stock(1, 2)
        with pytest.raises(InsufficientStockError):
            w.remove_stock(1, 5, "Пицца")

    def test_add_stock_none_id_raises(self):
        w = Warehouse()
        with pytest.raises(ValidationError):
            w.add_stock(None, 10)

    def test_add_stock_zero_raises(self):
        w = Warehouse()
        with pytest.raises(ValidationError):
            w.add_stock(1, 0)

    def test_str(self):
        w = Warehouse()
        w.add_stock(1, 5)
        assert "1" in str(w)
