from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    stock: int

    class Config:
        from_attributes = True


class CartProduct(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class Cart(BaseModel):
    id: int
    products: list[CartProduct]

    class Config:
        from_attributes = True


class OrderProduct(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class Order(BaseModel):
    id: int
    total: float
    products: list[OrderProduct]

    class Config:
        from_attributes = True
