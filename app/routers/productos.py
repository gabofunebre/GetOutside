# app/routers/productos.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from ..core.templates import templates
from sqlalchemy.orm import Session
from .. import crud, schemas, database, models

router = APIRouter(prefix="/productos", tags=["Productos"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/new", response_class=HTMLResponse)
def new_product_form(request: Request, db: Session = Depends(get_db)):
    catalogos = db.query(models.Catalogo).all()
    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "catalogos": catalogos}
    )

@router.post("/", response_model=schemas.ProductoOut)
def create_producto(p: schemas.ProductoCreate, db: Session = Depends(get_db)):
    return crud.create_producto(db, p)

@router.get("/{codigo}", response_model=schemas.ProductoOut)
def read_producto(codigo: str, db: Session = Depends(get_db)):
    prod = crud.get_producto(db, codigo)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod
