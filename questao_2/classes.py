from pydantic import BaseModel
from typing import Dict


class Product(BaseModel):
    name: str
    price: float
    stock: int

    def check_stock(self, quantity):
        return self.stock >= quantity


class Cart(BaseModel):
    products: Dict[Product, int] = {}

    def add_product(self, product, quantity: int = 1):
        if not product.check_stock(quantity):
            raise Exception("Not enough stock for this product!")

        if not product in self.products.keys():
            self.products[product] = quantity
        else:
            self.products[product] += quantity

    def remove_product(self, product, quantity: int = 1):
        if product in self.products:
            if self.products[product] <= quantity:
                del self.products[product]
            else:
                self.products[product] -= quantity

    def calculate_total(self):
        total = 0
        for product, quantity in self.products.items():
            total += product.price * quantity

        return total

    def finish(self):
        total = self.calculate_total()

        for product, quantity in self.products.items():
            product.stock -= quantity

        order = Order(self.products, total)
        return order


class Order(BaseModel):
    products: Dict
    total: float
    