from abc import ABC, abstractmethod
from domain.model import Order, LoyaltyLevel


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, order: Order, loyalty_level: LoyaltyLevel) -> float:
        """Возвращает процент скидки"""


class NoDiscount(DiscountStrategy):
    def apply(self, order: Order, loyalty_level: LoyaltyLevel) -> float:
        return 0.0


class LoyaltyDiscount(DiscountStrategy):
    def apply(self, order: Order, loyalty_level: LoyaltyLevel) -> float:
        discounts = {
            LoyaltyLevel.BRONZE: 0,
            LoyaltyLevel.SILVER: 5,
            LoyaltyLevel.GOLD: 15,
        }
        return discounts.get(loyalty_level, 0)
