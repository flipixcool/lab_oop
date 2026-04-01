from typing import Callable, TypeVar
from sqlalchemy.orm import Session
from repository.base import Repository
from repository.models_orm import CustomerORM, ProductORM, OrderORM, OrderItemORM
from domain.model import Customer, Product, Order, OrderItem, LoyaltyLevel, OrderStatus

T = TypeVar('T')


def _customer_to_orm(c: Customer) -> CustomerORM:
    return CustomerORM(
        id=c.id,
        name=c.name,
        email=c.email,
        loyalty_level=c.loyalty_level.value,
        created_at=c.created_at,
    )


def _orm_to_customer(orm: CustomerORM) -> Customer:
    c = Customer.__new__(Customer)
    c.id = orm.id
    c.name = orm.name
    c.email = orm.email
    c._loyalty_level = LoyaltyLevel(orm.loyalty_level)
    c.created_at = orm.created_at
    return c


def _product_to_orm(p: Product) -> ProductORM:
    return ProductORM(
        id=p.id,
        name=p.name,
        price=p.price,
        category=p.category,
        is_active=p.is_active,
    )


def _orm_to_product(orm: ProductORM) -> Product:
    p = Product.__new__(Product)
    p.id = orm.id
    p.name = orm.name
    p._price = orm.price
    p.category = orm.category
    p.is_active = orm.is_active
    return p


def _order_to_orm(o: Order) -> OrderORM:
    orm = OrderORM(
        id=o.id,
        customer_id=o.customer_id,
        status=o.status.value,
        discount=o.discount,
        created_at=o.created_at,
    )
    orm.items = [
        OrderItemORM(
            order_id=o.id,
            product_id=item.product.id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        for item in o.items
    ]
    return orm


def _orm_to_order(orm: OrderORM, products: dict[str, Product]) -> Order:
    items = [
        _orm_item_to_domain(i, products[i.product_id])
        for i in orm.items
        if i.product_id in products
    ]
    o = Order.__new__(Order)
    o.id = orm.id
    o.customer_id = orm.customer_id
    o.status = OrderStatus(orm.status)
    o.discount = orm.discount
    o.created_at = orm.created_at
    o.items = items
    return o


def _orm_item_to_domain(orm: OrderItemORM, product: Product) -> OrderItem:
    item = OrderItem.__new__(OrderItem)
    item.product = product
    item.quantity = orm.quantity
    item.unit_price = orm.unit_price
    return item


class CustomerPostgresRepository(Repository[Customer]):
    def __init__(self, session: Session):
        self._session = session

    def add(self, entity: Customer) -> Customer:
        self._session.add(_customer_to_orm(entity))
        self._session.commit()
        return entity

    def get(self, id: str) -> Customer | None:
        orm = self._session.get(CustomerORM, id)
        return _orm_to_customer(orm) if orm else None

    def update(self, entity: Customer) -> Customer:
        orm = self._session.get(CustomerORM, entity.id)
        if not orm:
            from domain.exceptions import CustomerNotFoundError
            raise CustomerNotFoundError(f"Customer '{entity.id}' not found")
        orm.name = entity.name
        orm.email = entity.email
        orm.loyalty_level = entity.loyalty_level.value
        self._session.commit()
        return entity

    def delete(self, id: str) -> bool:
        orm = self._session.get(CustomerORM, id)
        if not orm:
            return False
        self._session.delete(orm)
        self._session.commit()
        return True

    def find_all(self) -> list[Customer]:
        return [_orm_to_customer(o) for o in self._session.query(CustomerORM).all()]

    def find_by(self, predicate: Callable[[Customer], bool]) -> list[Customer]:
        return [c for c in self.find_all() if predicate(c)]


class ProductPostgresRepository(Repository[Product]):
    def __init__(self, session: Session):
        self._session = session

    def add(self, entity: Product) -> Product:
        self._session.add(_product_to_orm(entity))
        self._session.commit()
        return entity

    def get(self, id: str) -> Product | None:
        orm = self._session.get(ProductORM, id)
        return _orm_to_product(orm) if orm else None

    def update(self, entity: Product) -> Product:
        orm = self._session.get(ProductORM, entity.id)
        if not orm:
            from domain.exceptions import ProductNotFoundError
            raise ProductNotFoundError(f"Product '{entity.id}' not found")
        orm.name = entity.name
        orm.price = entity.price
        orm.category = entity.category
        orm.is_active = entity.is_active
        self._session.commit()
        return entity

    def delete(self, id: str) -> bool:
        orm = self._session.get(ProductORM, id)
        if not orm:
            return False
        self._session.delete(orm)
        self._session.commit()
        return True

    def find_all(self) -> list[Product]:
        return [_orm_to_product(o) for o in self._session.query(ProductORM).all()]

    def find_by(self, predicate: Callable[[Product], bool]) -> list[Product]:
        return [p for p in self.find_all() if predicate(p)]


class OrderPostgresRepository(Repository[Order]):
    def __init__(self, session: Session):
        self._session = session

    def _load_products(self, items: list[OrderItemORM]) -> dict[str, Product]:
        ids = {i.product_id for i in items}
        orms = self._session.query(ProductORM).filter(ProductORM.id.in_(ids)).all()
        return {o.id: _orm_to_product(o) for o in orms}

    def add(self, entity: Order) -> Order:
        self._session.add(_order_to_orm(entity))
        self._session.commit()
        return entity

    def get(self, id: str) -> Order | None:
        orm = self._session.get(OrderORM, id)
        if not orm:
            return None
        return _orm_to_order(orm, self._load_products(orm.items))

    def update(self, entity: Order) -> Order:
        orm = self._session.get(OrderORM, entity.id)
        if not orm:
            from domain.exceptions import InvalidOrderError
            raise InvalidOrderError(f"Order '{entity.id}' not found")
        orm.status = entity.status.value
        orm.discount = entity.discount
        self._session.commit()
        return entity

    def delete(self, id: str) -> bool:
        orm = self._session.get(OrderORM, id)
        if not orm:
            return False
        self._session.delete(orm)
        self._session.commit()
        return True

    def find_all(self) -> list[Order]:
        orms = self._session.query(OrderORM).all()
        return [_orm_to_order(o, self._load_products(o.items)) for o in orms]

    def find_by(self, predicate: Callable[[Order], bool]) -> list[Order]:
        return [o for o in self.find_all() if predicate(o)]
