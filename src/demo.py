from model import Customer, OrderStorage

# Создаем объекты
print(f"Всего клиентов до: {Customer.total_customers}")
ivan = Customer("Иван", 25)
maria = Customer("Мария", 30)
alex = Customer("Алекс", 20)
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

# Добавляем заказы
ivan.add_order([{"pizza": 2, "price": 500}], 1000)
maria.add_order([{"coffee": 1, "price": 200}], 200)


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

for order in found.get_orders():
    print(f"  {order}")

# Ошибка при создании заказа
print("\n--- Ошибка при создании заказа ---")
try:
    ivan.add_order([{"pizza": -3, "price": 500}], -1500)
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
order1 = ivan.add_order([{"burger": 1, "price": 300}], 300)
order2 = ivan.add_order([{"fries": 2, "price": 150}], 300)
storage.add_order(order1)
storage.add_order(order2)
print(f"Всего заказов в хранилище: {len(storage.get_all_orders())}")
print(f"Поиск по ID: {storage.find_by_id(order1.order_id)}")


print(len(maria.get_orders()))