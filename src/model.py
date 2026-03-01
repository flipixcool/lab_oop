from cryptography.fernet import Fernet
from uuid import uuid4
from typing import List, Dict
import base64
import re
from datetime import datetime


class Order:
    def __init__(self, order_id: str, items: List[Dict], total: float, discount: float = 0, original_total: float | None = None):
        if not order_id or not order_id.strip():
            raise ValueError("ID заказа не может быть пустым")
        if not items:
            raise ValueError("Список товаров не может быть пустым")
        if total is None:
            raise ValueError("Сумма заказа не может быть пустой")
        if total < 0:
            raise ValueError("Сумма заказа не может быть меньше 0")

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
        if self.discount == "active":
            return f"Заказ #{self.order_id} | Сумма: {self.original_total}₽ → {self.total}₽ (скидка: {self.discount}₽)"
        return f"Заказ #{self.order_id} | Сумма: {self.total}₽"


class OrderStorage:
    """Класс-хранилище для всех заказов"""

    _instance = None
    orders: List[Order] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

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


class CustomerManager:
    """Менеджер для шифрования/дешифрования ID"""

    def __init__(self):
        key = Fernet.generate_key()
        self.cipher = Fernet(key)

    def _encrypt_id(self, customer_id: str) -> str:
        """Шифрует ID в base64 строку"""
        encrypted = self.cipher.encrypt(customer_id.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def _decrypt_id(self, encrypted_id: str) -> str:
        """Расшифровывает ID"""
        encrypted = base64.urlsafe_b64decode(encrypted_id.encode())
        return self.cipher.decrypt(encrypted).decode()


class Customer:
    _manager = CustomerManager()
    _storage = OrderStorage()
    total_customers = 0

    @staticmethod
    def _validate_not_empty(value: str, field_name: str):
        if not value or not value.strip():
            raise ValueError(f"{field_name} не может быть пустым")

    def __init__(self, name: str, age: int, card_status: str = "active"):
        Customer.total_customers += 1

        self._validate_not_empty(name, "Имя")
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ]+$", name):
            raise ValueError("Имя должно содержать только буквы")
        if age is None:
            raise ValueError("Возраст не может быть пустым")
        if not 0 <= age <= 110:
            raise ValueError("Возраст должен быть от 0 до 110")
        self._validate_not_empty(card_status, "Статус карты")

        self.name = name
        self.age = age
        self.card_status = card_status
        self._raw_id = str(uuid4())  # Реальный ID
        self.customer_id = self._encrypt_id()  # Зашифрованный ID

    @property
    def raw_id(self) -> str:
        """Только для админа! Расшифрованный ID"""
        return self._manager._decrypt_id(self.customer_id)

    @raw_id.setter
    def raw_id(self, value):
        raise AttributeError("raw_id нельзя менять")

    @property
    def card_status(self) -> str:
        return self._card_status

    @card_status.setter
    def card_status(self, value: str):
        self._validate_not_empty(value, "Статус карты")
        self._card_status = value

    def _encrypt_id(self) -> str:
        """Приватный метод шифрования"""
        return self._manager._encrypt_id(self._raw_id)

    def add_order(self, items: List[Dict]):
        """Добавляет заказ к клиенту через Storage"""
        original_total = 0
        for item in items:
            for key, value in item.items():
                if key != "price":
                    original_total += item["price"] * value
        
        discount = 0
        total = original_total
        if self.card_status == "active":
            discount = original_total * 0.15
            total = original_total - discount
        
        order_id = f"{self._raw_id[:8]}-{Customer._storage.get_count()+1}"
        order = Order(order_id, items, total, discount, original_total)
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
            if o.order_id.startswith(self._raw_id[:8])
        ]

    def total_orders(self) -> Dict:
        """Возвращает полную корзину клиента со всеми заказами"""
        orders = self.get_orders()
        total_sum = sum(order.total for order in orders)
        all_items = []
        for order in orders:
            all_items.extend(order.items)
        return {
            "orders": orders,
            "items": all_items,
            "total": total_sum,
            "discount": 0,
            "final_total": total_sum
        }

    def apply_discount(self) -> Dict:
        """Применяет скидку 15% если card_status = 'active'"""
        cart = self.total_orders()
        if self.card_status == "active":
            discount = cart["total"] * 0.15
            final_total = cart["total"] - discount
            return {
                "orders": cart["orders"],
                "items": cart["items"],
                "total": cart["total"],
                "discount": discount,
                "final_total": final_total
            }
        return cart

    def __str__(self):
        return f"{self.name} (ID: {self.customer_id[:16]}...)"

    def __eq__(self, other):
        if isinstance(other, Customer):
            return self.customer_id == other.customer_id
        return False

    def __repr__(self):
        return f"Customer('{self.name}', {self.age}, '{self.customer_id}')"
