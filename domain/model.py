from uuid import uuid4
from typing import List, Dict
import re
from datetime import datetime
from domain.validators import Validators, ValidationError
from domain.exceptions import InsufficientStockError

CARD_STATUSES = ["active", "inactive", "blocked"]


class Customer:
    total_customers = 0

    def __init__(self, name: str, age: int, card_status: str = "active"):
        Validators.validate_not_empty(name, "Имя")
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ]+$", name):
            raise ValidationError("Имя должно содержать только буквы", "Имя")
        Validators.validate_range(age, "Возраст", 0, 110)
        Validators.validate_enum(card_status, "Статус карты", CARD_STATUSES)

        Customer.total_customers += 1
        self.customer_id = str(uuid4())
        self.name = name
        self.age = age
        self._card_status = card_status

    @property
    def card_status(self) -> str:
        return self._card_status

    @card_status.setter
    def card_status(self, value: str):
        Validators.validate_enum(value, "Статус карты", CARD_STATUSES)
        self._card_status = value

    def activate(self):
        self.card_status = "active"

    def close(self):
        self.card_status = "blocked"

    def upgrade(self):
        if self.card_status == "inactive":
            self.card_status = "active"

    def __str__(self):
        return f"{self.name} (ID: {self.customer_id})"

    def __eq__(self, other):
        if isinstance(other, Customer):
            return self.customer_id == other.customer_id
        return False

    def __repr__(self):
        return f"Customer('{self.name}', {self.age}, '{self.card_status}')"


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
        if quantity == 0:
            raise ValidationError("Количество должно быть больше 0", "Количество")

        self.product = product
        self.quantity = quantity

    @property
    def total(self) -> float:
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity} = {self.total}₽"


class Order:
    def __init__(self, customer: Customer, items: List[OrderItem]):
        Validators.validate_type(customer, "Клиент", Customer)
        Validators.validate_not_empty(items, "Список товаров")

        self.order_id = str(uuid4())
        self.customer = customer
        self.items = items
        self.status = "pending"
        self.created_at = datetime.now()

    @property
    def total(self) -> float:
        return sum(item.total for item in self.items)

    @property
    def final_total(self) -> float:
        if self.customer.card_status == "active":
            return self.total * 0.85
        return self.total

    def complete(self):
        self.status = "completed"

    def cancel(self):
        self.status = "cancelled"

    def __str__(self):
        discount_info = f" → {self.final_total}₽ (скидка 15%)" if self.customer.card_status == "active" else ""
        return f"Заказ #{self.order_id[:8]} | {self.customer.name} | {self.total}₽{discount_info} | {self.status}"


class Warehouse:
    def __init__(self):
        self._stock: Dict[str, int] = {}

    def add_stock(self, product: Product, quantity: int):
        Validators.validate_type(product, "Товар", Product)
        Validators.validate_positive(quantity, "Количество")
        self._stock[product.product_id] = self._stock.get(product.product_id, 0) + quantity

    def get_stock(self, product: Product) -> int:
        return self._stock.get(product.product_id, 0)

    def reserve(self, product: Product, quantity: int):
        available = self.get_stock(product)
        if quantity > available:
            raise InsufficientStockError(product.name, quantity, available)
        self._stock[product.product_id] -= quantity

    def __str__(self):
        return f"Warehouse: {len(self._stock)} позиций на складе"
