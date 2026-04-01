from abc import ABC, abstractmethod
from domain.model import Order, LoyaltyLevel


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, order: Order, loyalty_level: LoyaltyLevel) -> float:
        """Возвращает итоговую сумму заказа после применения скидки"""


class NoDiscount(DiscountStrategy):
    def apply(self, order: Order, loyalty_level: LoyaltyLevel) -> float:
        return order.total


class LoyaltyDiscount(DiscountStrategy):
    def apply(self, order: Order, loyalty_level: LoyaltyLevel) -> float:
        discounts = {
            LoyaltyLevel.BRONZE: 0,
            LoyaltyLevel.SILVER: 5,
            LoyaltyLevel.GOLD: 15,
        }
        discount_percent = discounts.get(loyalty_level, 0)
        return order.total * (1 - discount_percent / 100)
