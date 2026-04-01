from domain.model import Customer, Product, Order, OrderItem, Warehouse
from domain.exceptions import CustomerNotFoundError, ProductNotFoundError, InvalidOrderError
from domain.strategies import DiscountStrategy
from repository.base import Repository


class OrderService:
    def __init__(
        self,
        order_repo: Repository[Order],
        customer_repo: Repository[Customer],
        product_repo: Repository[Product],
        warehouse: Warehouse,
    ):
        self._order_repo = order_repo
        self._customer_repo = customer_repo
        self._product_repo = product_repo
        self._warehouse = warehouse

    def create_order(
        self,
        customer_id: str,
        items_data: list[dict],
        discount_strategy: DiscountStrategy,
    ) -> Order:
        if not self._customer_repo.get(customer_id):
            raise CustomerNotFoundError(f"Customer '{customer_id}' not found")

        items = []
        for data in items_data:
            product = self._product_repo.get(data["product_id"])
            if not product:
                raise ProductNotFoundError(f"Product '{data['product_id']}' not found")
            quantity = data["quantity"]
            self._warehouse.remove_stock(product.id, quantity, product.name)
            items.append(OrderItem(product, quantity))

        order = Order(customer_id, items)
        return self._order_repo.add(order)

    def add_item_to_order(self, order_id: str, product_id: str, quantity: int) -> Order:
        order = self._order_repo.get(order_id)
        if not order:
            raise InvalidOrderError(f"Order '{order_id}' not found")
        product = self._product_repo.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        self._warehouse.remove_stock(product.id, quantity, product.name)
        order.add_item(OrderItem(product, quantity))
        return self._order_repo.update(order)

    def get_order(self, order_id: str) -> Order | None:
        return self._order_repo.get(order_id)

    def get_customer_orders(self, customer_id: str) -> list[Order]:
        return self._order_repo.find_by(lambda o: o.customer_id == customer_id)

    def change_order_status(self, order_id: str, new_status: str) -> Order:
        order = self._order_repo.get(order_id)
        if not order:
            raise InvalidOrderError(f"Order '{order_id}' not found")
        order.change_status(new_status)
        return self._order_repo.update(order)

    def calculate_total_with_discount(
        self, order_id: str, customer_id: str, discount_strategy: DiscountStrategy
    ) -> float:
        order = self._order_repo.get(order_id)
        if not order:
            raise InvalidOrderError(f"Order '{order_id}' not found")
        customer = self._customer_repo.get(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer '{customer_id}' not found")
        return discount_strategy.apply(order, customer.loyalty_level)
