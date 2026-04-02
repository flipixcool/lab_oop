from sqlalchemy import Integer, String, Float, Boolean, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from db import Base
from domain.model import OrderStatus, LoyaltyLevel


class CustomerORM(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    loyalty_level: Mapped[str] = mapped_column(
        SAEnum(LoyaltyLevel, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=LoyaltyLevel.BRONZE.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    orders: Mapped[list["OrderORM"]] = relationship("OrderORM", back_populates="customer")


class ProductORM(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    order_items: Mapped[list["OrderItemORM"]] = relationship("OrderItemORM", back_populates="product")


class OrderORM(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(OrderStatus, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
        default=OrderStatus.PENDING.value,
    )
    discount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    customer: Mapped["CustomerORM"] = relationship("CustomerORM", back_populates="orders")
    items: Mapped[list["OrderItemORM"]] = relationship("OrderItemORM", back_populates="order", cascade="all, delete-orphan")


class OrderItemORM(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["OrderORM"] = relationship("OrderORM", back_populates="items")
    product: Mapped["ProductORM"] = relationship("ProductORM", back_populates="order_items")
