from db import SessionLocal
from domain.model import Warehouse
from repository.postgres import CustomerPostgresRepository, ProductPostgresRepository, OrderPostgresRepository
from service import CustomerService, ProductService, OrderService
from presentation.cli import CLI

session = SessionLocal()

customer_repo = CustomerPostgresRepository(session)
product_repo = ProductPostgresRepository(session)
order_repo = OrderPostgresRepository(session)
warehouse = Warehouse()

customer_service = CustomerService(customer_repo)
product_service = ProductService(product_repo, warehouse)
order_service = OrderService(order_repo, customer_repo, product_repo, warehouse)

cli = CLI(customer_service, product_service, order_service)
cli.run()
