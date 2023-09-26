from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    stock = Column(Integer)


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    products = relationship("CartProduct", backref="cart")


class CartProduct(Base):
    __tablename__ = "cart_product"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    cart_id = Column(Integer, ForeignKey("cart.id"))
    quantity = Column(Integer)


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float)
    products = relationship("OrderProduct", backref="order")


class OrderProduct(Base):
    __tablename__ = "order_product"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    product_id = Column(Integer, ForeignKey("product.id"))
    quantity = Column(Integer)
