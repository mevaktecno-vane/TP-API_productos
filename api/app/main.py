from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 👉 URL de la base de datos
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@db:5432/productos_db"

# Configuración SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de base de datos


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)


# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="API de Productos")

# Modelo Pydantic para validación


class ProductCreate(BaseModel):
    name: str
    description: str

# Endpoint raíz


@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de productos 🚀"}

# Endpoint para listar productos


@app.get("/products")
def get_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

# Endpoint para crear producto


@app.post("/products")
def create_product(product: ProductCreate):
    db = SessionLocal()
    db_product = Product(name=product.name, description=product.description)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

# Endpoint para actualizar producto


@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductCreate):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        db.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Actualizar valores
    db_product.name = product.name
    db_product.description = product.description

    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

# Endpoint para eliminar producto


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        db.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(db_product)
    db.commit()
    db.close()
    return {"message": f"Producto con id {product_id} eliminado correctamente"}
