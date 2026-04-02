from enum import Enum
from typing import List, Dict
from datetime import datetime
from domain.validators import Validators
from domain.exceptions import ValidationError, InsufficientStockError


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class LoyaltyLevel(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class Customer:
    total_customers = 0

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        loyalty_level: str = "bronze",
        id: int | None = None,
        created_at: datetime | None = None,
    ):
        Validators.validate_not_empty(first_name, "Имя")
        Validators.validate_not_empty(last_name, "Фамилия")
        Validators.validate_not_empty(email, "Email")

        Customer.total_customers += 1
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self._loyalty_level = LoyaltyLevel(loyalty_level)
        self.created_at = created_at or datetime.now()

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def loyalty_level(self) -> LoyaltyLevel:
        return self._loyalty_level

    @loyalty_level.setter
    def loyalty_level(self, value: str):
        self._loyalty_level = LoyaltyLevel(value)

    def activate(self):
        self.loyalty_level = LoyaltyLevel.BRONZE.value

    def upgrade(self):
        if self._loyalty_level == LoyaltyLevel.BRONZE:
            self.loyalty_level = LoyaltyLevel.SILVER.value
        elif self._loyalty_level == LoyaltyLevel.SILVER:
            self.loyalty_level = LoyaltyLevel.GOLD.value

    def close(self):
        self.loyalty_level = LoyaltyLevel.BRONZE.value

    def __str__(self):
        from domain.utils import format_customer_id
        id_str = format_customer_id(self.id) if self.id else "C-???"
        return f"{self.name} <{self.email}> (ID: {id_str})"

    def __eq__(self, other):
        if isinstance(other, Customer):
            return self.id == other.id
        return False

    def __repr__(self):
        return f"Customer('{self.first_name}', '{self.last_name}', '{self.email}', {self.loyalty_level})"


class Product:
    def __init__(
        self,
        name: str,
        price: float,
        category: str,
        id: int | None = None,
        is_active: bool = True,
    ):
        Validators.validate_not_empty(name, "Название товара")
        Validators.validate_positive(price, "Цена")
        Validators.validate_not_empty(category, "Категория")

        self.id = id
        self.name = name
        self._price = price
        self.category = category
        self.is_active = is_active

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        Validators.validate_positive(value, "Цена")
        self._price = value

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def __str__(self):
        return f"{self.name} — {self._price}₽ [{self.category}]"

    def __repr__(self):
        return f"Product('{self.name}', {self._price}, '{self.category}')"

    def __lt__(self, other: "Product") -> bool:
        return self._price < other._price


class OrderItem:
    def __init__(self, product: Product, quantity: int):
        Validators.validate_type(product, "Товар", Product)
        Validators.validate_positive(quantity, "Количество")

        self.product = product
        self.quantity = quantity
        self.unit_price = product.price

    @property
    def subtotal(self) -> float:
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity} = {self.subtotal}₽"


class Order:
    def __init__(
        self,
        customer_id: int,
        items: List[OrderItem],
        status: str = "pending",
        discount: float = 0.0,
        id: int | None = None,
        created_at: datetime | None = None,
    ):
        if customer_id is None:
            from domain.exceptions import ValidationError
            raise ValidationError("ID клиента", "не может быть None")
        Validators.validate_not_empty(items, "Список товаров")
        Validators.validate_non_negative(discount, "Скидка")
        Validators.validate_range(discount, "Скидка", 0, 100)

        self.id = id
        self.customer_id = customer_id
        self.items = items
        self.status = OrderStatus(status)
        self.discount = discount
        self.created_at = created_at or datetime.now()
        self._total: float | None = None

    @property
    def total(self) -> float:
        if self._total is not None:
            return self._total
        return sum(item.subtotal for item in self.items)

    @total.setter
    def total(self, value: float):
        self._total = value

    def change_status(self, new_status: str):
        self.status = OrderStatus(new_status)

    def add_item(self, item: OrderItem):
        Validators.validate_type(item, "Позиция заказа", OrderItem)
        self.items.append(item)

    def __lt__(self, other: "Order") -> bool:
        return self.created_at < other.created_at

    def __str__(self):
        from domain.utils import format_order_id
        id_str = format_order_id(self.id) if self.id else "O-???"
        final_total = self.total * (1 - self.discount / 100)
        return f"Заказ {id_str} | {final_total:.2f}₽ ({self.discount}% скидка) | {self.status.value}"


class Warehouse:
    def __init__(self):
        self._stock: Dict[int, int] = {}

    def add_stock(self, product_id: int, quantity: int):
        if product_id is None:
            raise ValidationError("ID товара не может быть пустым", "ID товара")
        Validators.validate_positive(quantity, "Количество")
        self._stock[product_id] = self._stock.get(product_id, 0) + quantity

    def get_stock(self, product_id: int) -> int:
        return self._stock.get(product_id, 0)

    def has_enough(self, product_id: int, quantity: int) -> bool:
        return self.get_stock(product_id) >= quantity

    def remove_stock(self, product_id: int, quantity: int, product_name: str = ""):
        available = self.get_stock(product_id)
        if quantity > available:
            raise InsufficientStockError(product_name or str(product_id), quantity, available)
        self._stock[product_id] -= quantity

    def __str__(self):
        return f"Warehouse: {len(self._stock)} позиций на складе"
