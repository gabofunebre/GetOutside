from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from ..core.templates import templates
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database

router = APIRouter(prefix="/payment_methods", tags=["Payment Methods"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1) Formulario HTML para agregar (GET /payment_methods/new)
@router.get("/new", response_class=HTMLResponse)
def new_payment_method_form(request: Request):
    return templates.TemplateResponse(
        "payment_method_form.html",
        {"request": request}
    )

# 2) Página HTML para editar (GET /payment_methods/edit)
@router.get("/edit", response_class=HTMLResponse)
def edit_payment_methods(request: Request, db: Session = Depends(get_db)):
    methods = crud.get_payment_methods(db)
    return templates.TemplateResponse(
        "payment_method_edit.html",
        {"request": request, "payment_methods": methods}
    )

# 3) API JSON para crear (POST /payment_methods)
@router.post("/", response_model=schemas.PaymentMethodOut)
def create_payment_method(pm: schemas.PaymentMethodCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_payment_method(db, pm)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4) API JSON para listar (GET /payment_methods)
@router.get("/", response_model=List[schemas.PaymentMethodOut])
def list_payment_methods(db: Session = Depends(get_db)):
    return crud.get_payment_methods(db)

# 5) API DELETE /payment_methods/id/{id}
@router.delete("/id/{id}")
def delete_payment_method(id: int, db: Session = Depends(get_db)):
    try:
        if not crud.delete_payment_method_by_id(db, id):
            raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
        return {"message": "Eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 6) API JSON para actualizar (PUT /payment_methods/id/{id})
@router.put("/id/{id}", response_model=schemas.PaymentMethodOut)
def update_payment_method(id: int, pm_data: schemas.PaymentMethodCreate, db: Session = Depends(get_db)):
    updated = crud.update_payment_method_by_id(db, id, pm_data.name)
    if not updated:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")
    return updated