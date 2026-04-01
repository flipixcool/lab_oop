from uuid import uuid4
from enum import Enum
from typing import List, Dict
import re
from datetime import datetime
from domain.validators import Validators
from domain.exceptions import ValidationError, InsufficientStockError


class LoyaltyLevel(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class OrderStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Customer:
    total_customers = 0

    def __init__(self, name: str, age: int, loyalty_level: LoyaltyLevel = LoyaltyLevel.ACTIVE):
        Validators.validate_not_empty(name, "Имя")
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ]+$", name):
            raise ValidationError("Имя должно содержать только буквы", "Имя")
        Validators.validate_range(age, "Возраст", 0, 110)
        Validators.validate_type(loyalty_level, "Уровень лояльности", LoyaltyLevel)

        Customer.total_customers += 1
        self.customer_id = str(uuid4())
        self.name = name
        self.age = age
        self._loyalty_level = loyalty_level

    @property
    def loyalty_level(self) -> LoyaltyLevel:
        return self._loyalty_level

    @loyalty_level.setter
    def loyalty_level(self, value: LoyaltyLevel):
        Validators.validate_type(value, "Уровень лояльности", LoyaltyLevel)
        self._loyalty_level = value

    def activate(self):
        self.loyalty_level = LoyaltyLevel.ACTIVE

    def close(self):
        self.loyalty_level = LoyaltyLevel.BLOCKED

    def upgrade(self):
        if self.loyalty_level == LoyaltyLevel.INACTIVE:
            self.loyalty_level = LoyaltyLevel.ACTIVE

    def __str__(self):
        return f"{self.name} (ID: {self.customer_id})"

    def __eq__(self, other):
        if isinstance(other, Customer):
            return self.customer_id == other.customer_id
        return False

    def __repr__(self):
        return f"Customer('{self.name}', {self.age}, {self.loyalty_level})"


class Product:
    def __init__(self, name: str, price: float):
        Validators.validate_not_empty(name, "Название товара")
        Validators.validate_positive(price, "Цена")

        self.product_id = str(uuid4())
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} — {self.price}₽"

    def __repr__(self):
        return f"Product('{self.name}', {self.price})"


class OrderItem:
    def __init__(self, product: Product, quantity: int):
        Validators.validate_type(product, "Товар", Product)
        Validators.validate_positive(quantity, "Количество")

        self.product = product
        self.quantity = quantity

    @property
    def subtotal(self) -> float:
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity} = {self.subtotal}₽"


class Order:
    def __init__(self, customer_id: str, items: List[OrderItem]):
        Validators.validate_not_empty(customer_id, "ID клиента")
        Validators.validate_not_empty(items, "Список товаров")

        self.order_id = str(uuid4())
        self.customer_id = customer_id
        self.items = items
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    def change_status(self, new_status: OrderStatus):
        Validators.validate_type(new_status, "Статус заказа", OrderStatus)
        self.status = new_status

    def __str__(self):
        return f"Заказ #{self.order_id[:8]} | {self.total}₽ | {self.status.value}"


class Warehouse:
    def __init__(self):
        self._stock: Dict[str, int] = {}

    def add_stock(self, product: Product, quantity: int):
        Validators.validate_type(product, "Товар", Product)
        Validators.validate_positive(quantity, "Количество")
        self._stock[product.product_id] = self._stock.get(product.product_id, 0) + quantity

    def get_stock(self, product_id: str) -> int:
        return self._stock.get(product_id, 0)

    def remove_stock(self, product_id: str, quantity: int, product_name: str = ""):
        available = self.get_stock(product_id)
        if quantity > available:
            raise InsufficientStockError(product_name or product_id, quantity, available)
        self._stock[product_id] -= quantity

    def __str__(self):
        return f"Warehouse: {len(self._stock)} позиций на складе"
