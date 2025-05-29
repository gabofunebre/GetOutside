# app/routers/payment_methods.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from app.core.templates import templates
from app.core.currencies import (
    TOP_CURRENCIES,
    CURRENCY_LABELS,
)  # Importa desde archivo central
from app.crud.paymentMet import (
    create_payment_method,
    get_payment_methods,
    delete_payment_method_by_id,
    update_payment_method_by_id,
)
from app.schemas import pago
from app.core.deps import get_db


router = APIRouter(prefix="/payment_methods", tags=["Payment Methods"])


# --- Vista: Formulario para crear nuevo medio de pago ---
@router.get("/new", response_class=HTMLResponse)
def new_payment_method_form(request: Request):
    """Renderiza el formulario de creación de método de pago."""
    return templates.TemplateResponse("payment_method_form.html", {"request": request})


# --- Vista: Tabla de medios de pago para edición ---
@router.get("/edit", response_class=HTMLResponse)
def edit_payment_methods(request: Request, db: Session = Depends(get_db)):
    """Renderiza el listado para edición de medios de pago."""
    methods = get_payment_methods(db)
    return templates.TemplateResponse(
        "payment_method_edit.html", {"request": request, "payment_methods": methods}
    )


# --- API: Crear método de pago ---
@router.post("/", response_model=pago.PaymentMethodOut)
def crear_payment_method(pm: pago.PaymentMethodCreate, db: Session = Depends(get_db)):
    """Crea y devuelve un nuevo medio de pago."""
    try:
        return create_payment_method(db, pm)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- API: Listar medios de pago ---
@router.get("/", response_model=List[pago.PaymentMethodOut])
def list_payment_methods(db: Session = Depends(get_db)):
    """Devuelve todos los medios de pago registrados."""
    return get_payment_methods(db)


# --- API: Eliminar medio de pago ---
@router.delete("/id/{id}")
def delete_payment_method(id: int, db: Session = Depends(get_db)):
    """Elimina un método de pago si no está en uso."""
    try:
        if not delete_payment_method_by_id(db, id):
            raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
        return {"message": "Eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- API: Actualizar medio de pago ---
@router.put("/id/{id}", response_model=pago.PaymentMethodOut)
def update_payment_method(
    id: int, pm_data: pago.PaymentMethodCreate, db: Session = Depends(get_db)
):
    """Actualiza nombre y moneda de un medio de pago."""
    try:
        updated = update_payment_method_by_id(db, id, pm_data.name, pm_data.currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")
    return updated


# --- API: Monedas admitidas con bandera ---
@router.get("/currencies")
def get_supported_currencies():
    """Devuelve las monedas admitidas con su etiqueta visual."""
    return TOP_CURRENCIES


@router.get("/currencies_labels")
def get_supported_currencies_labels():
    """Devuelve diccionario con las etiquetas de las monedas admitidas."""
    return CURRENCY_LABELS
