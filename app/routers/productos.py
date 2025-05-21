# app/routers/productos.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from ..core.templates import templates
from sqlalchemy.orm import Session
from .. import crud, schemas, database, models

router = APIRouter(prefix="/productos", tags=["Productos"])


# === MODELO AUXILIAR ===
class StockUpdate(BaseModel):
    stock_agregado: int


# === DEPENDENCIA DE DB ===
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === FORMULARIO HTML PARA AGREGAR PRODUCTO ===
@router.get("/new", response_class=HTMLResponse)
def new_product_form(request: Request, db: Session = Depends(get_db)):
    catalogos = db.query(models.Catalogo).all()
    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "catalogos": catalogos}
    )


# === CREAR PRODUCTO (API JSON) ===
@router.post("/", response_model=schemas.ProductoOut)
def create_producto(p: schemas.ProductoCreate, db: Session = Depends(get_db)):
    return crud.create_producto(db, p)


# === CONSULTAR PRODUCTO POR CÓDIGO GET (PARA URLs) ===
@router.get("/{codigo}", response_model=schemas.ProductoOut)
def read_producto(codigo: str, db: Session = Depends(get_db)):
    prod = crud.get_producto(db, codigo)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod


# === ACTUALIZAR STOCK POR CÓDIGO GET ===
@router.put("/{codigo}", response_model=schemas.ProductoOut)
def agregar_stock(codigo: str, data: StockUpdate, db: Session = Depends(get_db)):
    prod = crud.get_producto(db, codigo)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return crud.agregar_stock(db, prod, data.stock_agregado)


# === ACTUALIZAR STOCK POR ID ===
@router.put("/id/{producto_id}", response_model=schemas.ProductoOut)
def agregar_stock_por_id(producto_id: int, data: StockUpdate, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter_by(id=producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return crud.agregar_stock(db, prod, data.stock_agregado)


# === CONSULTAR PRODUCTO POR ID ===
@router.get("/id/{id}", response_model=schemas.ProductoOut)
def read_producto_by_id(id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Producto).filter(models.Producto.id == id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod


# === CONSULTAR PRODUCTO POR CÓDIGO (SIN ERRORES PARA FRONTEND) ===
@router.get("/")
def safe_read_producto(codigo: str | None = None, db: Session = Depends(get_db)):
    if codigo is None:
        raise HTTPException(status_code=400, detail="Debe proporcionar un código.")
    prod = crud.get_producto(db, codigo)
    if not prod:
        return {"exists": False}
    return prod


# === DEBUG HEADERS ===
@router.get("/debug/headers")
def debug_headers(request: Request):
    return {
        "host": request.headers.get("host"),
        "x-forwarded-proto": request.headers.get("x-forwarded-proto"),
        "url": str(request.url),
        "client": request.client.host
    }
