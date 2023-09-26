from fastapi import FastAPI, HTTPException, Depends
from starlette.responses import RedirectResponse
from database import SessionLocal, engine
from sqlalchemy.orm import Session

import models
import schemas


models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Compras",
    description="API para comprar de um e-commerce",
)


# Para pegar a Sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redireciona para a documentação do FastAPI
@app.get("/")
async def main():
    return RedirectResponse(url="/docs/")


# Rota listar produtos
@app.get("/products/")
async def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    if not products:
        return HTTPException(status_code=404, detail="Products not found")

    return products


# Rota listar produto por id
@app.get("/products/{product_id}/")
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).one_or_none()
    if not product:
        return HTTPException(status_code=404, detail="Product not found")

    return product


# Rota criar produto
@app.post("/products/")
async def create_product(product: schemas.Product, db: Session = Depends(get_db)):
    product = models.Product(**product.model_dump())
    if not product:
        return HTTPException(status_code=404, detail="Product not created")
    
    db.add(product)
    db.commit()
    db.refresh(product)

    return {"Message": f"Product '{product.name}' created successfully"}


# Rota deletar produto
@app.delete("/products/{product_id}/")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).one_or_none()
    if not product:
        return HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()

    return {"Message": f"Product '{product.name}' deleted successfully"}


# Rota atualizar produto
@app.put("/products/{product_id}/")
async def update_product(product_id: int, new_product: schemas.Product, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).one_or_none()
    if not product:
        return HTTPException(status_code=404, detail="Product not found")
    
    for key, value in vars(new_product).items():
        setattr(product, key, value) if value else None
        
    db.commit()
    db.refresh(product)

    return {"Message": f"Product '{product.name}' updated successfully"}


# Rota para listar carrinhos
@app.get("/cart/")
async def get_carts(db: Session = Depends(get_db)):
    carts = db.query(models.Cart).all()
    if not carts:
        return HTTPException(status_code=404, detail="Carts not found")

    carts_list = []
    for cart in carts:
        dict_cart = schemas.Cart.model_validate(cart).model_dump()
        carts_list.append(dict_cart)
        
    return carts_list if carts_list else carts


# Rota para listar carrinho por id
@app.get("/cart/{cart_id}/")
async def get_cart_by_id(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).one_or_none()
    if not cart:
        return HTTPException(status_code=404, detail="Cart not found")
    
    dict_cart = schemas.Cart.model_validate(cart).model_dump()
    return dict_cart if dict_cart else cart


# Rota adicionar produto ao carrinho
@app.post("/cart/{product_id}/")
async def add_product_to_cart(cart_id: int, product_id: int, quantity: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).one_or_none()
    if not product:
        return HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < quantity:
        return HTTPException(status_code=404, detail="Not enough stock for this product")

    product.stock -= quantity
        
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).one_or_none()
    if not cart:
        cart = models.Cart(id=cart_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        
    cart_product = db.query(models.CartProduct).filter(models.CartProduct.cart_id == cart_id).filter(models.CartProduct.product_id == product_id).one_or_none()
    if cart_product:
        cart_product.quantity += quantity
    else:
        cart_product = models.CartProduct(cart_id=cart_id, product_id=product_id, quantity=quantity)
        db.add(cart_product)
        
    db.commit()
    db.refresh(cart_product)

    return {"Message": f"Product '{product.name}' added to cart successfully"}


# Rota remover produto do carrinho
@app.delete("/cart/{product_id}/")
async def remove_product_from_cart(cart_id: int, product_id: int, quantity: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).one_or_none()
    if not product:
        return HTTPException(status_code=404, detail="Product not found")

    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).one_or_none()
    if not cart:
        return HTTPException(status_code=404, detail="Cart not found")
    
    cart_product = db.query(models.CartProduct).filter(models.CartProduct.cart_id == cart_id).filter(models.CartProduct.product_id == product_id).one_or_none()
    if not cart_product:
        return HTTPException(status_code=404, detail="Product not found in cart")
    
    if cart_product.quantity < quantity:
        return HTTPException(status_code=404, detail="Not enough quantity of this product in cart")
     
    if cart_product.quantity == quantity:
        db.delete(cart_product)
        db.commit()
    else:
        cart_product.quantity -= quantity
        db.commit()
        db.refresh(cart_product)
    
    product.stock += quantity
    return {"Message": f"{quantity} unit(s) of '{product.name}' removed from cart successfully"}


# Rota para calcular o total do carrinho
@app.get("/cart/total/{cart_id}/}")
async def calculate_total(cart_id: int, db: Session = Depends(get_db), utils = False):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).one_or_none()
    if not cart:
        return HTTPException(status_code=404, detail="Cart not found")
    
    product_ids_quantity = [(cart_product.product_id, cart_product.quantity) for cart_product in cart.products]
    
    total = 0
    for id, quantity in product_ids_quantity:
        product = db.query(models.Product).filter(models.Product.id == id).one_or_none()
        total += product.price * quantity

    if utils:
        return total, product_ids_quantity
    
    return {"Message": f"Total: {total}"}


# Rota para finalizar o pedido
@app.post("/order/{cart_id}/")
async def finish_order(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).one_or_none()
    if not cart:
        return HTTPException(status_code=404, detail="Cart not found")
    
    total, product_ids_quantity = await calculate_total(cart.id, db, True)
    
    # Criar o pedido
    order = models.Order(total=total)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Limpar o carrinho
    db.query(models.CartProduct).filter(models.CartProduct.cart_id == cart.id).delete()
    db.query(models.Cart).filter(models.Cart.id == cart_id).delete()
    db.commit()

    for id, quantity in product_ids_quantity:
        product = db.query(models.Product).filter(models.Product.id == id).one_or_none()
        if product.stock == 0:
            del product
            db.commit()
            db.refresh(product)
            
        order_product = models.OrderProduct(order_id=order.id, product_id=id, quantity=quantity)
        db.add(order_product)
        db.commit()
        db.refresh(order_product)
    
    return {"Message": f"Order '{order.id}' from cart '{cart.id}' created successfully"}


# Rota para listar pedido por id
@app.get("/order/{order_id}/")
async def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).one_or_none()
    if not order:
        return HTTPException(status_code=404, detail="Order not found")
    
    dict_order = schemas.Order.model_validate(order).model_dump()
    return dict_order if dict_order else order
