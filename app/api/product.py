from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List
import shutil, os, json

from app.db.database import SessionLocal
from app.schemas.schemas import ProductCreate, ProductRead, ProductUpdate
from app.crud import product as crud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/products/", response_model=ProductRead)
async def create_product_with_pdf(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image_url: str = Form(...),
    stock: int = Form(...),
    is_pack: bool = Form(False),
    pack_ids: str = Form("[]"),  # JSON string
    is_new: bool = Form(False),
    pdf: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    product_data = ProductCreate(
        name=name,
        description=description,
        price=price,
        image_url=image_url,
        stock=stock,
        is_pack=is_pack,
        is_new=is_new,
        pack_ids=json.loads(pack_ids)
    )
    product = crud.create_product(db, product_data)

    if pdf and pdf.filename.endswith(".pdf"):
        os.makedirs("ebooks", exist_ok=True)
        path = os.path.join("ebooks", f"{product.id}.pdf")
        with open(path, "wb") as f:
            shutil.copyfileobj(pdf.file, f)

    return product

@router.put("/products/{product_id}", response_model=ProductRead)
async def update_product_with_pdf(
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image_url: str = Form(...),
    stock: int = Form(...),
    is_pack: bool = Form(False),
    pack_ids: str = Form("[]"),
    is_new: bool = Form(False),
    pdf: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    updated = crud.update_product(db, product_id, ProductUpdate(
        name=name,
        description=description,
        price=price,
        image_url=image_url,
        stock=stock,
        is_pack=is_pack,
        is_new=is_new,
        pack_ids=json.loads(pack_ids)
    ))

    if not updated:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if pdf and pdf.filename.endswith(".pdf"):
        os.makedirs("ebooks", exist_ok=True)
        path = os.path.join("ebooks", f"{product_id}.pdf")
        with open(path, "wb") as f:
            shutil.copyfileobj(pdf.file, f)

    return updated

@router.get("/products/", response_model=List[ProductRead])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_products(db, skip, limit)

@router.get("/products/{product_id}", response_model=ProductRead)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.post("/products/{product_id}/add_to_cart")
def add_to_cart(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if product.stock < 1:
        raise HTTPException(status_code=400, detail="Stock insuficiente")
    product.stock -= 1
    db.commit()
    db.refresh(product)
    return {"message": "Producto añadido al carrito", "stock_actual": product.stock}

@router.post("/products/{product_id}/return_to_stock")
def return_product_to_stock(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    product.stock += 1
    db.commit()
    db.refresh(product)
    return {"message": "Producto devuelto al stock", "stock_actual": product.stock}
