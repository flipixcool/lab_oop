from cryptography.fernet import Fernet
from uuid import uuid4
from typing import List, Dict
import base64
import re
from datetime import datetime


class Order:
    def __init__(self, order_id: str, items: List[Dict], total: float):
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
        self.created_at = datetime.now()

    def __str__(self):
        return f"Заказ #{self.order_id} | Сумма: {self.total}₽"


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

    def __init__(self, name: str, age: int, card_status: str = "active"):
        try:
            re.match(r"^[a-zA-Zа-яА-ЯёЁ]+$", name).group()
        except AttributeError:
            raise ValueError(
                "Имя должно содержать только буквы латинского или русского алфавита"
            )
        self.name = name

        try:
            if age < 0 or age > 110:
                raise ValueError()
        except ValueError:
            raise ValueError("Возраст должен быть от 0 до 110")
        self.age = age
        self.card_status = card_status
        self._raw_id = str(uuid4())  # Реальный ID
        self.customer_id = self._encrypt_id()  # Зашифрованный ID
        self.orders: List[Order] = []  # Список заказов

    @property
    def raw_id(self) -> str:
        """Только для админа! Расшифрованный ID"""
        return self._manager._decrypt_id(self.customer_id)

    def _encrypt_id(self) -> str:
        """Приватный метод шифрования"""
        return self._manager._encrypt_id(self._raw_id)

    def add_order(self, items: List[Dict], total: float):
        """Добавляет заказ к клиенту"""
        order_id = f"{self._raw_id[:8]}-{len(self.orders)+1}"
        order = Order(order_id, items, total)
        self.orders.append(order)
        return order

    def delete_order(self, order_id: str) -> bool:
        """Удаляет заказ по ID. Возвращает True если успешно"""
        for i, order in enumerate(self.orders):
            if order.order_id == order_id:
                self.orders.pop(i)
                return True
        return False

    def get_orders(self) -> List[Order]:
        """Возвращает заказы клиента"""
        return self.orders

    def __str__(self):
        return f"{self.name} (ID: {self.customer_id[:16]}...)"

    def __repr__(self):
        return f"Customer('{self.name}', {self.age}, '{self.customer_id}')"
