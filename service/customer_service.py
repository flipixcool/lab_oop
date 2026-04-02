from domain.model import Customer, LoyaltyLevel
from domain.exceptions import CustomerNotFoundError
from repository.base import Repository


class CustomerService:
    def __init__(self, repo: Repository[Customer]):
        self._repo = repo

    def create_customer(self, first_name: str, last_name: str, email: str, loyalty: str = "bronze") -> Customer:
        customer = Customer(first_name, last_name, email, loyalty)
        return self._repo.add(customer)

    def get_customer(self, id: str) -> Customer | None:
        return self._repo.get(id)

    def get_all_customers(self) -> list[Customer]:
        return self._repo.find_all()

    def upgrade_loyalty(self, customer_id: str) -> Customer:
        customer = self._repo.get(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer '{customer_id}' not found")
        customer.upgrade()
        return self._repo.update(customer)

    def find_by_name(self, first_name: str, last_name: str) -> list[Customer]:
        fn = first_name.lower()
        ln = last_name.lower()
        return self._repo.find_by(
            lambda c: c.first_name.lower() == fn and c.last_name.lower() == ln
        )

    def delete_customer(self, customer_id: str) -> bool:
        return self._repo.delete(customer_id)
