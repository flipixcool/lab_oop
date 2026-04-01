from uuid import uuid4
from typing import List, Dict
import re
from datetime import datetime
from validate import Validators


class Order:
    def __init__(self, order_id: str, items: List[Dict], total: float, discount: float = 0, original_total: float | None = None):
        Validators.validate_not_empty(order_id, "ID заказа")
        Validators.validate_not_empty(items, "Список товаров")
        Validators.validate_positive(total, "Сумма заказа")
        if total <= 0:
            raise ValueError("Сумма заказа должна быть больше 0")
        Validators.validate_positive(original_total if original_total else 0, "Оригинальная сумма")

        for item in items:
            if "price" not in item:
                raise ValueError("Цена товара обязательна")
            for key, value in item.items():
                if isinstance(value, (int, float)) and value < 0:
                    if key == "price":
                        raise ValueError("Цена не может быть меньше 0")
                    else:
                        raise ValueError("Количество вещей не может быть меньше 0")
        self.order_id = order_id
        self.items = items
        self.total = total
        self.discount = discount
        self.original_total = original_total if original_total is not None else total
        self.created_at = datetime.now()

    def __str__(self):
        if self.discount > 0:
            return f"Заказ #{self.order_id} | Сумма: {self.original_total}₽ → {self.total}₽ (скидка: {self.discount}₽)"
        return f"Заказ #{self.order_id} | Сумма: {self.total}₽"


class OrderStorage:
    """Класс-хранилище для всех заказов"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'orders'):
            self.orders: List[Order] = []

    def add_order(self, order: Order):
        self.orders.append(order)

    def get_order(self, order_id: str) -> Order | None:
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def remove_order(self, order_id: str) -> bool:
        for i, order in enumerate(self.orders):
            if order.order_id == order_id:
                self.orders.pop(i)
                return True
        return False

    def find_by_id(self, order_id: str) -> Order | None:
        return self.get_order(order_id)

    def get_all_orders(self) -> List[Order]:
        return self.orders

    def get_count(self) -> int:
        return len(self.orders)


class Customer:
    _storage = OrderStorage()
    total_customers = 0

    def __init__(self, name: str, age: int, card_status: str = "active"):
        Validators.validate_not_empty(name, "Имя")
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ]+$", name):
            raise ValueError("Имя должно содержать только буквы")
        Validators.validate_range(age, "Возраст", 0, 110)
        Validators.validate_not_empty(card_status, "Статус карты")

        Customer.total_customers += 1

        self.name = name
        self.age = age
        self.card_status = card_status
        self.customer_id = str(uuid4())

    @property
    def card_status(self) -> str:
        return self._card_status

    @card_status.setter
    def card_status(self, value: str):
        Validators.validate_not_empty(value, "Статус карты")
        self._card_status = value

    def activate(self):
        """Активирует карту"""
        self.card_status = "active"
        print(f"Карта клиента {self.name} активирована")

    def close(self):
        """Блокирует карту"""
        self.card_status = "blocked"
        print(f"Карта клиента {self.name} заблокирована")

    def upgrade(self):
        """Повышает статус карты (если была inactive -> active)"""
        if self.card_status == "inactive":
            self.card_status = "active"
            print(f"Карта клиента {self.name} обновлена до active")
        else:
            print(f"Карта клиента {self.name} уже в статусе {self.card_status}")

    def add_order(self, items: List[Dict]):
        """Добавляет заказ к клиенту через Storage"""
        original_total = sum(
            item["price"] * v
            for item in items
            for k, v in item.items()
            if k != "price"
        )

        order_id = f"{self.customer_id[:8]}-{Customer._storage.get_count()+1}"
        order = Order(order_id, items, original_total, 0, original_total)
        Customer._storage.add_order(order)
        return order

    def delete_order(self, order_id: str) -> bool:
        """Удаляет заказ по ID через Storage"""
        return Customer._storage.remove_order(order_id)

    def get_orders(self) -> List[Order]:
        """Возвращает заказы клиента"""
        return [
            o
            for o in Customer._storage.get_all_orders()
            if o.order_id.startswith(self.customer_id[:8])
        ]

    def total_orders(self) -> Dict:
        """Возвращает полную корзину клиента со всеми заказами"""
        orders = self.get_orders()
        total_sum = sum(order.total for order in orders)
        all_items = []
        for order in orders:
            all_items.extend(order.items)
        
        discount = 0
        final_total = total_sum
        if self.card_status == "active":
            discount = total_sum * 0.15
            final_total = total_sum - discount
        
        return {
            "orders": orders,
            "items": all_items,
            "total": total_sum,
            "discount": discount,
            "final_total": final_total
        }

    def print_cart(self):
        """Выводит корзину клиента в красивом формате"""
        cart = self.total_orders()
        print(f"\n--- Корзина {self.name} ---")
        print(f"Товары: {cart['items']}")
        print(f"Итого: {cart['total']}₽")
        if cart['discount'] > 0:
            print(f"Скидка (15%): -{cart['discount']}₽")
        print(f"К оплате: {cart['final_total']}₽")
        print(f"Статус карты: {self.card_status}")

    def apply_discount(self) -> Dict:
        """Применяет скидку 15% если card_status = 'active'"""
        return self.total_orders()

    def __str__(self):
        return f"{self.name} (ID: {self.customer_id})"

    def __eq__(self, other):
        if isinstance(other, Customer):
            return self.customer_id == other.customer_id
        return False

    def __repr__(self):
        return f"Customer('{self.name}', {self.age}, '{self.customer_id}')"
