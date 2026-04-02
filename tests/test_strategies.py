import pytest
from domain.model import Customer, Product, OrderItem, Order, LoyaltyLevel
from domain.strategies import NoDiscount, LoyaltyDiscount


@pytest.fixture
def order():
    customer = Customer("Иван", "Иванов", "ivan@mail.ru", "bronze")
    customer.id = 1
    product = Product("Пицца", 1000, "Еда")
    item = OrderItem(product, 1)
    return Order(customer.id, [item])


class TestNoDiscount:
    def test_returns_full_total(self, order):
        strategy = NoDiscount()
        assert strategy.apply(order, LoyaltyLevel.BRONZE) == 1000
        assert strategy.apply(order, LoyaltyLevel.GOLD) == 1000


class TestLoyaltyDiscount:
    def test_bronze_no_discount(self, order):
        strategy = LoyaltyDiscount()
        assert strategy.apply(order, LoyaltyLevel.BRONZE) == 1000

    def test_silver_five_percent(self, order):
        strategy = LoyaltyDiscount()
        assert strategy.apply(order, LoyaltyLevel.SILVER) == 950

    def test_gold_fifteen_percent(self, order):
        strategy = LoyaltyDiscount()
        assert strategy.apply(order, LoyaltyLevel.GOLD) == 850
