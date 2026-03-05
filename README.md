# Лабораторная работа: Объектно-ориентированное программирование

## Класс Customer

Класс для управления клиентами с поддержкой шифрования ID, заказов и скидок.

### Атрибуты
- `name` - имя клиента
- `age` - возраст клиента
- `card_status` - статус карты (active/inactive/blocked)
- `customer_id` - зашифрованный ID клиента
- `raw_id` - расшифрованный ID (только для чтения)

### Методы
- `activate()` - активирует карту
- `close()` - блокирует карту
- `upgrade()` - повышает статус карты (inactive → active)
- `add_order(items)` - добавляет заказ
- `delete_order(order_id)` - удаляет заказ
- `get_orders()` - возвращает все заказы клиента
- `total_orders()` - возвращает полную корзину с расчётом скидки
- `print_cart()` - выводит корзину в консоль
- `apply_discount()` - применяет скидку 15% для активных карт

### Пример использования
```python
customer = Customer("Иван", 25, "active")
customer.add_order([{"pizza": 2, "price": 500}])
customer.print_cart()
```

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
