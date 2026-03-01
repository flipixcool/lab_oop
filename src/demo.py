# Создаём клиентов
from model import Customer

ivan = Customer("Иван", 25)
maria = Customer("Мария", 30)

# Добавляем заказы
ivan.add_order([{"pizza": 2, "price": 500}], 1000)
ivan.add_order([{"coffee": 1, "price": 200}], 200)


# Поиск по зашифрованному ID
def find_customer_by_id(customers: List[Customer], enc_id: str) -> Customer:
    for customer in customers:
        if customer.customer_id == enc_id:
            return customer
    return None


# Тестируем
customers = [ivan, maria]
found = find_customer_by_id(customers, ivan.customer_id)

for order in found.get_orders():
    print(f"  {order}")

try:
    ivan.add_order([{"pizza": -3, "price": 500}], -1500)
except ValueError as e:
    print(f"Ошибка: {e}")

for order in found.get_orders():
    print(order)

print(ivan.raw_id)
print()
