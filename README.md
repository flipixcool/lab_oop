# Лабораторная работа: Объектно-ориентированное программирование

## Задание на 3 балла

![aboba](/home/flipixcool/Documents/python/lab_oop/images/Screenshot_20260303_120042.png)

# Код demo.py

```python
from model import Customer, OrderStorage, Order

# Создаем объекты
print(f"Всего клиентов до: {Customer.total_customers}")
ivan = Customer("Иван", 25)
maria = Customer("Мария", 30)
print(f"Всего клиентов после: {Customer.total_customers}")

print("\n--- Задание на 3 ---")

# Демонстрация __str__ & __repr__
print("\n--- Демонстрация __str__ & __repr__ ---")
print(ivan)
print(ivan.__repr__())

# Сравниваем объекты
print("\n--- Сравнение объектов ---")
print(f"ivan == ivan: {ivan == ivan}")
print(f"ivan == maria: {ivan == maria}")

# Примеры ошибок при создании Customer
print("\n--- Ошибки при создании Customer ---")
try:
    bad_customer = Customer("Ivan123", 25)
except ValueError as e:
    print(f"Ошибка в имени: {e}")

try:
    bad_customer = Customer("Ivan", -5)
except ValueError as e:
    print(f"Ошибка в возрасте: {e}")

try:
    bad_customer = Customer("Ivan", 150)
except ValueError as e:
    print(f"Ошибка в возрасте: {e}")

# Ошибки при создании Order
print("\n--- Ошибки при создании Order ---")

try:
    bad_order = Order("", [{"pizza": 1, "price": 500}], 500)
except ValueError as e:
    print(f"Ошибка в ID: {e}")

try:
    bad_order = Order("1", [], 500)
except ValueError as e:
    print(f"Ошибка в товарах: {e}")

try:
    bad_order = Order("1", [{"pizza": 1, "price": 500}], 0)  # 0 to test empty check
except ValueError as e:
    print(f"Ошибка в сумме: {e}")

try:
    bad_order = Order("1", [{"pizza": 1, "price": 500}], -100)
except ValueError as e:
    print(f"Ошибка в сумме: {e}")

# Добавляем заказы
ivan.add_order([{"pizza": 2, "price": 500}])
maria.add_order([{"coffee": 1, "price": 200}])


# Поиск по зашифрованному ID
def find_customer_by_id(customers, enc_id: str) -> Customer | None:
    for customer in customers:
        if customer.customer_id == enc_id:
            return customer
    return None


# Тестируем
print("\n--- Заказы Иван ---")
customers = [ivan, maria]
found = find_customer_by_id(customers, ivan.customer_id)
assert found is not None

for order in found.get_orders():
    print(f"  {order}")

# Ошибка при создании заказа
print("\n--- Ошибка при создании заказа ---")
try:
    ivan.add_order([{"pizza": -3, "price": 500}])
except ValueError as e:
    print(f"Ошибка: {e}")

print("\n--- Заказы после неудачной попытки ---")
for order in found.get_orders():
    print(f"  {order}")

print(f"\nRaw ID: {ivan.raw_id}")

# Пример setter (запрет на изменение raw_id)
print("\n--- Попытка изменить raw_id ---")
try:
    ivan.raw_id = "new_id"
except AttributeError as e:
    print(f"Ошибка: {e}")

# OrderStorage (класс-хранилище заказов)
print("\n--- OrderStorage ---")
storage = OrderStorage()
order1 = ivan.add_order([{"burger": 1, "price": 300}])
order2 = ivan.add_order([{"fries": 2, "price": 150}])
storage.add_order(order1)
storage.add_order(order2)
print(f"Всего заказов в хранилище: {len(storage.get_all_orders())}")
print(f"Поиск по ID: {storage.find_by_id(order1.order_id)}")

# Пример getter и setter для card_status
print("\n--- Getter и Setter для card_status ---")
print(f"Статус карты: {ivan.card_status}")
ivan.card_status = "active"
print(f"После изменения: {ivan.card_status}")
try:
    ivan.card_status = ""
except ValueError as e:
    print(f"Ошибка: {e}")

# Методы изменения состояния
print("\n--- Методы изменения состояния ---")
petr = Customer("Пётр", 28, "inactive")
print(f"Статус карты Пётра: {petr.card_status}")
petr.activate()
print(f"После activate: {petr.card_status}")
petr.close()
print(f"После close: {petr.card_status}")

ivan.activate()
ivan.close()
ivan.upgrade()

print(len(maria.get_orders()))

ivan.print_cart()
maria.print_cart()
```
### Требования

- Один пользовательский класс
- Минимум 4 атрибута
- Закрытые поля (`_attribute`)
- Конструктор с базовой проверкой данных
- Свойства (`@property`) для чтения
- Минимум: `__str__`, `__eq__`
- Один простой бизнес-метод

### Реализация

```python
class Customer:
    def __init__(self, name: str, age: int, card_status: str = "active"):
        self.name = name
        self.age = age
        self.card_status = card_status
        self._raw_id = str(uuid4())
        self.customer_id = self._encrypt_id()

    def __str__(self):
        return f"{self.name} (ID: {self.customer_id[:16]}...)"

    def __eq__(self, other):
        if isinstance(other, Customer):
            return self.customer_id == other.customer_id
        return False

    def add_order(self, items: List[Dict]):
        """Добавляет заказ к клиенту"""
        ...
```

### Демонстрация

```python
# Создание объекта
ivan = Customer("Иван", 25)

# Вывод через print
print(ivan)  # Иван (ID: Z0FBQUFBQnBwSW5l...)

# Сравнение двух объектов
maria = Customer("Мария", 30)
print(ivan == maria)  # False
print(ivan == ivan)  # True

# Пример некорректного создания
try:
    bad_customer = Customer("Ivan123", 25)  # Ошибка в имени
except ValueError as e:
    print(f"Ошибка: {e}")
```

## Задание на 4 балла

### Дополнительные требования

- `__repr__`
- Минимум один setter с валидацией
- Атрибут класса
- Второй бизнес-метод
- Улучшенное форматирование вывода
- Валидация на тип и логическую корректность

### Реализация

```python
class Customer:
    total_customers = 0  # Атрибут класса

    def __init__(self, name: str, age: int, card_status: str = "active"):
        Customer.total_customers += 1
        # Валидация
        if not name or not name.strip():
            raise ValueError("Имя не может быть пустым")
        if not 0 <= age <= 110:
            raise ValueError("Возраст должен быть от 0 до 110")
        ...

    @property
    def card_status(self) -> str:
        return self._card_status

    @card_status.setter
    def card_status(self, value: str):
        if not value or not value.strip():
            raise ValueError("Статус карты не может быть пустым")
        self._card_status = value

    def __repr__(self):
        return f"Customer('{self.name}', {self.age}, '{self.customer_id}')"

    def get_orders(self) -> List[Order]:
        """Возвращает заказы клиента"""
        ...
```

### Демонстрация

```python
# Изменение свойства через setter
ivan.card_status = "blocked"
print(ivan.card_status)  # blocked

# Проверка ограничения
try:
    ivan.card_status = ""  # Ошибка
except ValueError as e:
    print(e)

# Доступ к атрибуту класса
print(Customer.total_customers)  # 2
print(ivan.total_customers)     # 2
```

---

## Задание на 5 баллов

### Дополнительные требования

- Валидация как отдельный метод
- Логическое состояние объекта
- Поведение, зависящее от состояния

### Реализация

#### Класс Validators


```python
class Validators:
    @staticmethod
    def validate_not_empty(value: Any, field_name: str):
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"{field_name} не может быть пустым")

    @staticmethod
    def validate_positive(value: float | int | None, field_name: str):
        if value is None:
            raise ValueError(f"{field_name} не может быть пустым")
        if value < 0:
            raise ValueError(f"{field_name} не может быть меньше 0")

    @staticmethod
    def validate_range(value: int | None, field_name: str, min_val: int, max_val: int):
        if value is None:
            raise ValueError(f"{field_name} не может быть пустым")
        if not min_val <= value <= max_val:
            raise ValueError(f"{field_name} должен быть от {min_val} до {max_val}")
```


### Методы изменения состояния


```python
def activate(self):
    """Активирует карту"""
    self.card_status = "active"

def close(self):
    """Блокирует карту"""
    self.card_status = "blocked"

def upgrade(self):
    """Повышает статус карты (inactive -> active)"""
    if self.card_status == "inactive":
        self.card_status = "active"
```


#### Поведение, зависящее от состояния


```python
def total_orders(self) -> Dict:
    """Возвращает корзину со скидкой 15% для active карты"""
    orders = self.get_orders()
    total_sum = sum(order.total for order in orders)
    
    discount = 0
    final_total = total_sum
    if self.card_status == "active":  # Зависит от состояния
        discount = total_sum * 0.15
        final_total = total_sum - discount
    
    return {
        "total": total_sum,
        "discount": discount,
        "final_total": final_total
    }
```


### Демонстрация


```python
# Создание клиента с inactive картой
petr = Customer("Пётр", 28, "inactive")

# Методы изменения состояния
petr.activate()   # Карта активирована
petr.close()     # Карта заблокирована
petr.upgrade()   # Только для inactive -> active

# Поведение зависит от состояния
ivan = Customer("Иван", 25, "active")
ivan.add_order([{"pizza": 2, "price": 500}])
cart = ivan.total_orders()
print(cart["final_total"])  # 850.0 (со скидкой 15%)

maria = Customer("Мария", 30, "blocked")
maria.add_order([{"coffee": 1, "price": 200}])
cart = maria.total_orders()
print(cart["final_total"])  # 200.0 (без скидки)
```
