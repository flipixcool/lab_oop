from service.customer_service import CustomerService
from service.product_service import ProductService
from service.order_service import OrderService
from domain.exceptions import ShopError
from domain.utils import format_customer_id, format_product_id, format_order_id, parse_id

class CLI:
    def __init__(self, customer_service: CustomerService, product_service: ProductService, order_service: OrderService):
        self._cs = customer_service
        self._ps = product_service
        self._os = order_service

    def run(self):
        while True:
            print("\n=== Добро пожаловать ===")
            print("  1. Пользователь")
            print("  2. Админ")
            print("  0. Выход")
            choice = input("Выбор: ").strip()
            if choice == "0":
                print("До свидания!")
                break
            elif choice == "1":
                self._user_panel()
            elif choice == "2":
                self._admin_panel()
            else:
                print("Неверный выбор.")

    # ── Панель пользователя ───────────────────────────────────────────────────

    def _user_panel(self):
        customer = self._login()
        if not customer:
            return

        print(f"\nДобро пожаловать, {customer.name}! (ID: {format_customer_id(customer.id)})")

        while True:
            print("\n=== Панель пользователя ===")
            print("  1. Показать товары")
            print("  2. Создать заказ")
            print("  3. Мои заказы")
            print("  4. Мои архивные заказы")
            print("  0. Выход")
            choice = input("Выбор: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._run(self._show_products)
            elif choice == "2":
                self._run(lambda: self._create_order_user(customer.id))
            elif choice == "3":
                self._run(lambda: self._my_orders(customer.id))
            elif choice == "4":
                self._run(lambda: self._my_archived_orders(customer.id))
            else:
                print("Неверный выбор.")

    def _login(self):
        print("\n--- Вход ---")
        first_name = input("Имя: ").strip()
        last_name = input("Фамилия: ").strip()
        if not first_name or not last_name:
            print("Отменено.")
            return None
        matches = self._cs.find_by_name(first_name, last_name)
        if not matches:
            print(f"Клиент '{first_name} {last_name}' не найден.")
            return None
        if len(matches) > 1:
            print("Найдено несколько клиентов:")
            for c in matches:
                print(f"  {format_customer_id(c.id)} | {c.name} | {c.email}")
            raw = input("Введите ID (например C-001): ").strip()
            try:
                cid = parse_id(raw)
                customer = next((c for c in matches if c.id == cid), None)
                if not customer:
                    print("Неверный ID.")
                    return None
                return customer
            except (ValueError, IndexError):
                print("Неверный формат.")
                return None
        return matches[0]

    def _show_products(self):
        products = [p for p in self._ps.get_all_products() if p.is_active]
        if not products:
            print("Товаров нет.")
            return
        for p in products:
            stock = self._ps.get_stock(p.id)
            print(f"  {format_product_id(p.id)} | {p.name} | {p.price}₽ | склад: {stock}")

    def _create_order_user(self, customer_id: int):
        items_data = []
        while True:
            raw_p = input("ID товара (например P-001, или Enter чтобы завершить): ").strip()
            if not raw_p:
                break
            quantity = int(input("Количество: ").strip())
            items_data.append({"product_id": parse_id(raw_p), "quantity": quantity})

        if not items_data:
            print("Нет позиций — заказ не создан.")
            return

        order = self._os.create_order(customer_id, items_data)
        print(f"Заказ создан: {order}")
        print(f"Скидка лояльности: {order.discount}%")
        print(f"Итого к оплате: {order.total * (1 - order.discount / 100):.2f}₽")

    def _my_orders(self, customer_id: int):
        orders = self._os.get_customer_orders(customer_id)
        if not orders:
            print("Заказов нет.")
            return
        for o in orders:
            print(f"  {o}")

    def _my_archived_orders(self, customer_id: int):
        archived = self._os.get_archived_orders(customer_id)
        if not archived:
            print("Архивных заказов нет.")
            return
        for o in archived:
            print(f"  {o}")

    # ── Панель администратора ─────────────────────────────────────────────────

    def _admin_panel(self):
        while True:
            print("\n=== Панель администратора ===")
            print("  1. Управление клиентами")
            print("  2. Управление товарами")
            print("  3. Управление складом")
            print("  4. Все заказы")
            print("  5. Изменить статус заказа")
            print("  6. Архив заказов")
            print("  0. Выход")
            choice = input("Выбор: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._run(self._customers_menu)
            elif choice == "2":
                self._run(self._products_menu)
            elif choice == "3":
                self._run(self._warehouse_menu)
            elif choice == "4":
                self._run(self._all_orders)
            elif choice == "5":
                self._run(self._change_order_status)
            elif choice == "6":
                self._run(self._archived_orders)
            else:
                print("Неверный выбор.")

    def _all_orders(self):
        orders = self._os.get_all_orders()
        if not orders:
            print("Заказов нет.")
            return
        for o in orders:
            final_total = o.total * (1 - o.discount / 100)
            print(f"  {format_order_id(o.id)} | {format_customer_id(o.customer_id)} | {o.status.value} | {final_total:.2f}₽ ({o.discount}% скидка)")

    # ── Клиенты ───────────────────────────────────────────────────────────────

    def _customers_menu(self):
        print("\n--- Клиенты ---")
        print("  1. Создать клиента")
        print("  2. Показать всех клиентов")
        print("  3. Удалить клиента")
        print("  4. Повысить уровень лояльности")
        choice = input("Выбор: ").strip()

        if choice == "1":
            first_name = input("Имя: ").strip()
            last_name = input("Фамилия: ").strip()
            email = input("Email: ").strip()
            loyalty = input("Уровень лояльности (bronze/silver/gold) [bronze]: ").strip() or "bronze"
            c = self._cs.create_customer(first_name, last_name, email, loyalty)
            print(f"Создан: {c}")

        elif choice == "2":
            customers = self._cs.get_all_customers()
            if not customers:
                print("Клиентов нет.")
            for c in customers:
                print(f"  {format_customer_id(c.id)} | {c.name} | {c.email} | {c.loyalty_level.value}")

        elif choice == "3":
            raw = input("ID клиента (например C-001): ").strip()
            if self._cs.delete_customer(parse_id(raw)):
                print("Удалён.")
            else:
                print("Клиент не найден.")

        elif choice == "4":
            raw = input("ID клиента (например C-001): ").strip()
            c = self._cs.upgrade_loyalty(parse_id(raw))
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
            print(f"Создан: {p} (ID: {format_product_id(p.id)})")

        elif choice == "2":
            products = self._ps.get_all_products()
            if not products:
                print("Товаров нет.")
            for p in products:
                stock = self._ps.get_stock(p.id)
                status = "активен" if p.is_active else "неактивен"
                print(f"  {format_product_id(p.id)} | {p} | склад: {stock} | {status}")

        elif choice == "3":
            raw = input("ID товара (например P-001): ").strip()
            new_price = float(input("Новая цена: ").strip())
            p = self._ps.update_price(parse_id(raw), new_price)
            print(f"Обновлён: {p}")

        elif choice == "4":
            raw = input("ID товара (например P-001): ").strip()
            p = self._ps.deactivate_product(parse_id(raw))
            print(f"Деактивирован: {p.name}")

    # ── Склад ─────────────────────────────────────────────────────────────────

    def _warehouse_menu(self):
        print("\n--- Склад ---")
        print("  1. Добавить товар на склад")
        print("  2. Проверить остаток")
        choice = input("Выбор: ").strip()

        if choice == "1":
            raw = input("ID товара (например P-001): ").strip()
            product_id = parse_id(raw)
            quantity = int(input("Количество: ").strip())
            self._ps.add_stock(product_id, quantity)
            print(f"Добавлено. Остаток: {self._ps.get_stock(product_id)}")

        elif choice == "2":
            raw = input("ID товара (например P-001): ").strip()
            product_id = parse_id(raw)
            print(f"Остаток: {self._ps.get_stock(product_id)}")

    # ── Заказы ────────────────────────────────────────────────────────────────

    def _change_order_status(self):
        raw = input("ID заказа (например O-001): ").strip()
        print("Статусы: pending / confirmed / shipped / delivered / cancelled")
        new_status = input("Новый статус: ").strip()
        order = self._os.change_order_status(parse_id(raw), new_status)
        print(f"Статус обновлён: {order.status.value}")

    def _archived_orders(self):
        archived = self._os.get_archived_orders()
        if not archived:
            print("Архив пуст.")
            return
        print("\n=== Архив заказов ===")
        for o in archived:
            final_total = o.total * (1 - o.discount / 100)
            print(f"  {format_order_id(o.id)} | {format_customer_id(o.customer_id)} | {o.status.value} | {final_total:.2f}₽ ({o.discount}% скидка)")

    # ── Вспомогательное ───────────────────────────────────────────────────────

    def _run(self, fn):
        try:
            fn()
        except ShopError as e:
            print(f"Ошибка: {e}")
        except (ValueError, KeyboardInterrupt):
            print("Отменено.")
