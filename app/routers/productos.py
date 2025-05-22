# app/routers/productos.py

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import crud, schemas, database, models
from ..core.templates import templates

router = APIRouter(prefix="/productos", tags=["Productos"])

# === DEPENDENCIA: Sesión de DB ===

def get_db():
    """Devuelve una sesión de base de datos y la cierra al terminar"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === MODELO AUXILIAR para actualizaciones parciales ===

class StockUpdate(BaseModel):
    stock_agregado: int  # cantidad a sumar o restar al stock_actual

# === CREACIÓN DE PRODUCTOS ===

@router.post("/", response_model=schemas.ProductoOut)
def create_producto(p: schemas.ProductoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo producto y lo devuelve"""
    return crud.create_producto(db, p)

# === FORMULARIO HTML ===

@router.get("/new", response_class=HTMLResponse)
def new_product_form(request: Request, db: Session = Depends(get_db)):
    """Renderiza la vista para crear un nuevo producto"""
    catalogos = db.query(models.Catalogo).all()
    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "catalogos": catalogos}
    )

# === CONSULTA DE PRODUCTOS POR ID ===

@router.get("/id/{producto_id}", response_model=schemas.ProductoOut)
def read_producto_by_id(producto_id: int, db: Session = Depends(get_db)):
    """Devuelve un producto dado su ID"""
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod

# === ACTUALIZAR STOCK POR ID ===

@router.put("/id/{producto_id}", response_model=schemas.ProductoOut)
def update_stock_by_id(producto_id: int, data: StockUpdate, db: Session = Depends(get_db)):
    """Ajusta el stock de un producto usando su ID"""
    prod = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return crud.agregar_stock(db, prod, data.stock_agregado)

# === LISTADO DE PRODUCTOS ===

@router.get("/", response_model=list[schemas.ProductoOut])  # ajusta vista/modelo si es necesario
def list_productos(db: Session = Depends(get_db)):
    """Devuelve todos los productos registrados"""
    return db.query(models.Producto).all()

# === RUTAS LEGACY (basadas en código), pueden eliminarse si no se usan ===

# @router.get("/{codigo}", response_model=schemas.ProductoOut)
# def read_producto_by_codigo(codigo: str, db: Session = Depends(get_db)):
#     """(Obsoleto) Devuelve un producto por su código (deprecated)"""
#     prod = crud.get_producto(db, producto_id=None)  # ya no funciona: refactorizar
#     if not prod:
#         raise HTTPException(status_code=404, detail="Producto no encontrado")
#     return prod

# @router.put("/{codigo}", response_model=schemas.ProductoOut)
# def update_stock_by_codigo(codigo: str, data: StockUpdate, db: Session = Depends(get_db)):
#     """(Obsoleto) Ajusta stock por código de producto (deprecated)"""
#     prod = db.query(models.Producto).filter(models.Producto.codigo_getoutside == codigo).first()
#     if not prod:
#         raise HTTPException(status_code=404, detail="Producto no encontrado")
#     return crud.agregar_stock(db, prod, data.stock_agregado)
