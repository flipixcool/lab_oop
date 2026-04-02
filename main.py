from db import SessionLocal
from repository.postgres import CustomerPostgresRepository, ProductPostgresRepository, OrderPostgresRepository, DBWarehouse
from service import CustomerService, ProductService, OrderService
from presentation.cli import CLI

session = SessionLocal()

try:
    customer_repo = CustomerPostgresRepository(session)
    product_repo = ProductPostgresRepository(session)
    order_repo = OrderPostgresRepository(session)
    warehouse = DBWarehouse(session)

    customer_service = CustomerService(customer_repo)
    product_service = ProductService(product_repo, warehouse)
    order_service = OrderService(order_repo, customer_repo, product_repo, warehouse)

    cli = CLI(customer_service, product_service, order_service)
    cli.run()
finally:
    session.close()
