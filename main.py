# from db import SessionLocal
# from repository.postgres import CustomerPostgresRepository, ProductPostgresRepository, OrderPostgresRepository, DBWarehouse
# from service import CustomerService, ProductService, OrderService
# from presentation.cli import CLI

# session = SessionLocal()

# try:
#     customer_repo = CustomerPostgresRepository(session)
#     product_repo = ProductPostgresRepository(session)
#     order_repo = OrderPostgresRepository(session)
#     warehouse = DBWarehouse(session)

#     customer_service = CustomerService(customer_repo)
#     product_service = ProductService(product_repo, warehouse)
#     order_service = OrderService(order_repo, customer_repo, product_repo, warehouse)

#     cli = CLI(customer_service, product_service, order_service)
#     cli.run()
# finally:
#     session.close()


def main():
    import sys, types
    sys.path.insert(0, '/tmp/lab_oop-main')

    from sqlalchemy.orm import DeclarativeBase
    fake_db = types.ModuleType('db')
    class Base(DeclarativeBase): pass
    fake_db.Base = Base
    fake_db.SessionLocal = None
    sys.modules['db'] = fake_db

    from repository.base import InMemoryRepository
    from domain.model import Product, OrderItem, Customer, Order

    product = Product('Ноутбук', 50000.0, 'Электроника')
    product.id = 1
    item = OrderItem(product, 2)
    customer = Customer('Иван', 'Иванов', 'ivan@test.com')
    customer.id = 1
    order = Order(customer.id, [item])

    # Используем InMemoryRepository вместо Postgres
    repo = InMemoryRepository()
    order = repo.add(order)

    repo.archive_order(order)


if __name__ == "__main__":
    main()
