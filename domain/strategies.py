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
    """15% скидка для активных клиентов"""

    def apply(self, order: Order, loyalty_level: LoyaltyLevel) -> float:
        if loyalty_level == LoyaltyLevel.ACTIVE:
            return order.total * 0.85
        return order.total
