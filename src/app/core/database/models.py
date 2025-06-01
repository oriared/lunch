import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
    name: Mapped[str]
    is_admin: Mapped[bool]
    is_active: Mapped[bool]
    joined_dt: Mapped[datetime.datetime]

    orders: Mapped[list['Order']] = relationship(back_populates='user', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, username={self.username!r})'


dish_category = Table(
    'dish_category',
    Base.metadata,
    Column('category_id', ForeignKey('category.id'), primary_key=True),
    Column('dish_id', ForeignKey('dish.id'), primary_key=True),
)


order_dish = Table(
    'order_dish',
    Base.metadata,
    Column('order_id', ForeignKey('order.id'), primary_key=True),
    Column('dish_id', ForeignKey('dish.id'), primary_key=True),
)


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str]
    name: Mapped[str]

    dishes: Mapped[list['Dish']] = relationship(secondary=dish_category, back_populates='categories')

    def __repr__(self) -> str:
        return f'Category(id={self.id!r}, name={self.name!r})'


class Dish(Base):
    __tablename__ = 'dish'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    weekday: Mapped[int | None]

    categories: Mapped[list['Category']] = relationship(secondary=dish_category, back_populates='dishes')
    orders: Mapped[list['Order']] = relationship(secondary=order_dish, back_populates='dishes')

    def __repr__(self) -> str:
        return f'Dish(id={self.id!r}, name={self.name!r})'


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('user.id'), index=True)
    date: Mapped[datetime.date]
    comment: Mapped[str]

    dishes: Mapped[list['Dish']] = relationship(secondary=order_dish, back_populates='orders')
    user: Mapped[Optional['User']] = relationship(back_populates='orders')

    def __repr__(self) -> str:
        return f'Order(id={self.id!r}, user_id={self.user_id!r})'
