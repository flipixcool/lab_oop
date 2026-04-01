from service.customer_service import CustomerService
from service.product_service import ProductService
from service.order_service import OrderService
from domain.strategies import LoyaltyDiscount, NoDiscount
from domain.exceptions import ShopError


class CLI:
    def __init__(self, customer_service: CustomerService, product_service: ProductService, order_service: OrderService):
        self._cs = customer_service
        self._ps = product_service
        self._os = order_service

    def run(self):
        menu = {
            "1": ("Управление клиентами", self._customers_menu),
            "2": ("Управление товарами", self._products_menu),
            "3": ("Управление складом", self._warehouse_menu),
            "4": ("Создать заказ", self._create_order),
            "5": ("Показать заказы клиента", self._show_customer_orders),
            "6": ("Изменить статус заказа", self._change_order_status),
            "0": ("Выход", None),
        }
        while True:
            print("\n=== Главное меню ===")
            for key, (label, _) in menu.items():
                print(f"  {key}. {label}")
            choice = input("Выбор: ").strip()
            if choice == "0":
                print("До свидания!")
                break
            if choice in menu:
                try:
                    menu[choice][1]()
                except ShopError as e:
                    print(f"Ошибка: {e}")
                except (ValueError, KeyboardInterrupt):
                    print("Отменено.")
            else:
                print("Неверный выбор.")

    # ── Клиенты ───────────────────────────────────────────────────────────────

    def _customers_menu(self):
        print("\n--- Клиенты ---")
        print("  1. Создать клиента")
        print("  2. Показать всех клиентов")
        print("  3. Удалить клиента")
        print("  4. Повысить уровень лояльности")
        choice = input("Выбор: ").strip()

        if choice == "1":
            name = input("Имя: ").strip()
            email = input("Email: ").strip()
            loyalty = input("Уровень лояльности (bronze/silver/gold) [bronze]: ").strip() or "bronze"
            c = self._cs.create_customer(name, email, loyalty)
            print(f"Создан: {c}")

        elif choice == "2":
            customers = self._cs.get_all_customers()
            if not customers:
                print("Клиентов нет.")
            for c in customers:
                print(f"  {c} | {c.loyalty_level.value}")

        elif choice == "3":
            customer_id = input("ID клиента: ").strip()
            if self._cs.delete_customer(customer_id):
                print("Удалён.")
            else:
                print("Клиент не найден.")

        elif choice == "4":
            customer_id = input("ID клиента: ").strip()
            c = self._cs.upgrade_loyalty(customer_id)
            print(f"Уровень лояльности: {c.loyalty_level.value}")

    # ── Товары ────────────────────────────────────────────────────────────────

    def _products_menu(self):
        print("\n--- Товары ---")
        print("  1. Создать товар")
        print("  2. Показать все товары")
        print("  3. Изменить цену")
        print("  4. Деактивировать товар")
        choice = input("Выбор: ").strip()

        if choice == "1":
            name = input("Название: ").strip()
            price = float(input("Цена: ").strip())
            category = input("Категория: ").strip()
            p = self._ps.create_product(name, price, category)
            print(f"Создан: {p} (ID: {p.id})")

        elif choice == "2":
            products = self._ps.get_all_products()
            if not products:
                print("Товаров нет.")
            for p in products:
                stock = self._ps.get_stock(p.id)
                status = "активен" if p.is_active else "неактивен"
                print(f"  {p} | склад: {stock} | {status} | ID: {p.id}")

        elif choice == "3":
            product_id = input("ID товара: ").strip()
            new_price = float(input("Новая цена: ").strip())
            p = self._ps.update_price(product_id, new_price)
            print(f"Обновлён: {p}")

        elif choice == "4":
            product_id = input("ID товара: ").strip()
            p = self._ps.deactivate_product(product_id)
            print(f"Деактивирован: {p.name}")

    # ── Склад ─────────────────────────────────────────────────────────────────

    def _warehouse_menu(self):
        print("\n--- Склад ---")
        print("  1. Добавить товар на склад")
        print("  2. Проверить остаток")
        choice = input("Выбор: ").strip()

        if choice == "1":
            product_id = input("ID товара: ").strip()
            quantity = int(input("Количество: ").strip())
            self._ps.add_stock(product_id, quantity)
            print(f"Добавлено. Остаток: {self._ps.get_stock(product_id)}")

        elif choice == "2":
            product_id = input("ID товара: ").strip()
            print(f"Остаток: {self._ps.get_stock(product_id)}")

    # ── Заказы ────────────────────────────────────────────────────────────────

    def _create_order(self):
        customer_id = input("ID клиента: ").strip()
        items_data = []
        while True:
            product_id = input("ID товара (или Enter чтобы завершить): ").strip()
            if not product_id:
                break
            quantity = int(input("Количество: ").strip())
            items_data.append({"product_id": product_id, "quantity": quantity})

        if not items_data:
            print("Нет позиций — заказ не создан.")
            return

        use_discount = input("Применить скидку лояльности? (y/n): ").strip().lower() == "y"
        strategy = LoyaltyDiscount() if use_discount else NoDiscount()

        order = self._os.create_order(customer_id, items_data, strategy)
        print(f"Заказ создан: {order}")

    def _show_customer_orders(self):
        customer_id = input("ID клиента: ").strip()
        orders = self._os.get_customer_orders(customer_id)
        if not orders:
            print("Заказов нет.")
            return
        for o in orders:
            print(f"  {o}")

    def _change_order_status(self):
        order_id = input("ID заказа: ").strip()
        print("Статусы: pending / confirmed / shipped / delivered / cancelled")
        new_status = input("Новый статус: ").strip()
        order = self._os.change_order_status(order_id, new_status)
        print(f"Статус обновлён: {order.status.value}")
