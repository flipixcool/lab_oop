from typing import Callable
from sqlalchemy.orm import Session
from repository.base import Repository
from repository.models_orm import CustomerORM, ProductORM, CategoryORM, OrderORM, OrderItemORM, WarehouseORM, ArchivedOrderORM
from domain.exceptions import InsufficientStockError
from domain.model import Customer, Product, Order, OrderItem, LoyaltyLevel, OrderStatus


def _customer_to_orm(c: Customer) -> CustomerORM:
    orm = CustomerORM(
        first_name=c.first_name,
        last_name=c.last_name,
        email=c.email,
        loyalty_level=c.loyalty_level.value,
        created_at=c.created_at,
    )
    if c.id:
        orm.id = c.id
    return orm


def _orm_to_customer(orm: CustomerORM) -> Customer:
    c = Customer.__new__(Customer)
    c.id = orm.id
    c.first_name = orm.first_name
    c.last_name = orm.last_name
    c.email = orm.email
    c._loyalty_level = LoyaltyLevel(orm.loyalty_level)
    c.created_at = orm.created_at
    return c


def _orm_to_product(orm: ProductORM) -> Product:
    p = Product.__new__(Product)
    p.id = orm.id
    p.name = orm.name
    p._price = orm.price
    p.category = orm.category_rel.name
    p.is_active = orm.is_active
    return p


def _order_to_orm(o: Order) -> OrderORM:
    orm = OrderORM(
        customer_id=o.customer_id,
        status=o.status.value,
        discount=o.discount,
        created_at=o.created_at,
    )
    if o.id:
        orm.id = o.id
    orm.items = [
        OrderItemORM(
            product_id=item.product.id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        for item in o.items
    ]
    return orm


def _orm_to_order(orm: OrderORM, products: dict[int, Product]) -> Order:
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
    o._total = None
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
        orm = _customer_to_orm(entity)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        entity.id = orm.id
        return entity

    def get(self, id: int) -> Customer | None:
        orm = self._session.get(CustomerORM, id)
        return _orm_to_customer(orm) if orm else None

    def update(self, entity: Customer) -> Customer:
        orm = self._session.get(CustomerORM, entity.id)
        if not orm:
            from domain.exceptions import CustomerNotFoundError
            raise CustomerNotFoundError(f"Customer '{entity.id}' not found")
        orm.first_name = entity.first_name
        orm.last_name = entity.last_name
        orm.email = entity.email
        orm.loyalty_level = entity.loyalty_level.value
        self._session.commit()
        return entity

    def delete(self, id: int) -> bool:
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

    def _get_or_create_category(self, name: str) -> CategoryORM:
        cat = self._session.query(CategoryORM).filter_by(name=name).first()
        if not cat:
            cat = CategoryORM(name=name)
            self._session.add(cat)
            self._session.flush()
        return cat

    def add(self, entity: Product) -> Product:
        cat = self._get_or_create_category(entity.category)
        orm = ProductORM(
            name=entity.name,
            price=entity.price,
            category_id=cat.id,
            is_active=entity.is_active,
        )
        if entity.id:
            orm.id = entity.id
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        entity.id = orm.id
        return entity

    def get(self, id: int) -> Product | None:
        orm = self._session.get(ProductORM, id)
        return _orm_to_product(orm) if orm else None

    def update(self, entity: Product) -> Product:
        orm = self._session.get(ProductORM, entity.id)
        if not orm:
            from domain.exceptions import ProductNotFoundError
            raise ProductNotFoundError(f"Product '{entity.id}' not found")
        cat = self._get_or_create_category(entity.category)
        orm.name = entity.name
        orm.price = entity.price
        orm.category_id = cat.id
        orm.is_active = entity.is_active
        self._session.commit()
        return entity

    def delete(self, id: int) -> bool:
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

    def _load_products(self, items: list[OrderItemORM]) -> dict[int, Product]:
        ids = {i.product_id for i in items}
        orms = self._session.query(ProductORM).filter(ProductORM.id.in_(ids)).all()
        return {o.id: _orm_to_product(o) for o in orms}

    def add(self, entity: Order) -> Order:
        orm = _order_to_orm(entity)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        entity.id = orm.id
        return entity

    def get(self, id: int) -> Order | None:
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

    def delete(self, id: int) -> bool:
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

    def archive_order(self, order: Order) -> Order:
        from datetime import datetime
        orm = self._session.get(OrderORM, order.id)
        if not orm:
            from domain.exceptions import InvalidOrderError
            raise InvalidOrderError(f"Order '{order.id}' not found")
        
        archived = ArchivedOrderORM(
            id=orm.id,
            customer_id=orm.customer_id,
            status=orm.status.value,
            discount=orm.discount,
            total=order.total,
            created_at=orm.created_at,
            archived_at=datetime.now(),
        )
        self._session.add(archived)
        
        for item_orm in orm.items:
            self._session.delete(item_orm)
        self._session.delete(orm)
        self._session.commit()
        return order

    def get_archived_orders(self, customer_id: int | None = None) -> list[Order]:
        query = self._session.query(ArchivedOrderORM)
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        orms = query.all()
        return [self._orm_to_archived_order(o) for o in orms]

    def _orm_to_archived_order(self, orm: ArchivedOrderORM) -> Order:
        o = Order.__new__(Order)
        o.id = orm.id
        o.customer_id = orm.customer_id
        o.status = OrderStatus(orm.status)
        o.discount = orm.discount
        o._total = orm.total
        o.created_at = orm.created_at
        o.items = []
        return o


class DBWarehouse:
    def __init__(self, session: Session):
        self._session = session

    def add_stock(self, product_id: int, quantity: int) -> None:
        row = self._session.get(WarehouseORM, product_id)
        if row:
            row.quantity += quantity
        else:
            row = WarehouseORM(product_id=product_id, quantity=quantity)
            self._session.add(row)
        self._session.commit()

    def get_stock(self, product_id: int) -> int:
        row = self._session.get(WarehouseORM, product_id)
        return row.quantity if row else 0

    def has_enough(self, product_id: int, quantity: int) -> bool:
        return self.get_stock(product_id) >= quantity

    def remove_stock(self, product_id: int, quantity: int, product_name: str = "") -> None:
        available = self.get_stock(product_id)
        if quantity > available:
            raise InsufficientStockError(product_name or str(product_id), quantity, available)
        row = self._session.get(WarehouseORM, product_id)
        row.quantity -= quantity
        self._session.commit()
