from domain.model import Product, Warehouse
from domain.exceptions import ProductNotFoundError
from repository.base import Repository


class ProductService:
    def __init__(self, repo: Repository[Product], warehouse: Warehouse):
        self._repo = repo
        self._warehouse = warehouse

    def create_product(self, name: str, price: float, category: str) -> Product:
        product = Product(name, price, category)
        return self._repo.add(product)

    def get_product(self, id: int) -> Product | None:
        return self._repo.get(id)

    def get_all_products(self) -> list[Product]:
        return self._repo.find_all()

    def update_price(self, product_id: int, new_price: float) -> Product:
        product = self._repo.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        product.price = new_price
        return self._repo.update(product)

    def add_stock(self, product_id: int, quantity: int) -> None:
        self._warehouse.add_stock(product_id, quantity)

    def get_stock(self, product_id: int) -> int:
        return self._warehouse.get_stock(product_id)

    def deactivate_product(self, product_id: int) -> Product:
        product = self._repo.get(product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found")
        product.deactivate()
        return self._repo.update(product)
