# app/routers/payment_methods.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from ..core.templates import templates
from .. import crud, schemas, database

# Lista completa de códigos ISO
ALL_CURRENCIES = [
    "AED","AFN","ALL","AMD","ANG","AOA","ARS","AUD","AWG","AZN",
    "BAM","BBD","BDT","BGN","BHD","BIF","BMD","BND","BOB","BRL",
    "BSD","BTN","BWP","BYN","BZD","CAD","CDF","CHF","CLP","CNY",
    "COP","CRC","CUC","CUP","CVE","CZK","DJF","DKK","DOP","DZD",
    "EGP","ERN","ETB","EUR","FJD","FKP","GBP","GEL","GGP","GHS",
    "GIP","GMD","GNF","GTQ","GYD","HKD","HNL","HRK","HTG","HUF",
    "IDR","ILS","IMP","INR","IQD","IRR","ISK","JEP","JMD","JOD",
    "JPY","KES","KGS","KHR","KMF","KPW","KRW","KWD","KYD","KZT",
    "LAK","LBP","LKR","LRD","LSL","LYD","MAD","MDL","MGA","MKD",
    "MMK","MNT","MOP","MRU","MUR","MVR","MWK","MXN","MYR","MZN",
    "NAD","NGN","NIO","NOK","NPR","NZD","OMR","PAB","PEN","PGK",
    "PHP","PKR","PLN","PYG","QAR","RON","RSD","RUB","RWF","SAR",
    "SBD","SCR","SDG","SEK","SGD","SHP","SLL","SOS","SRD","SSP",
    "STD","STN","SVC","SYP","SZL","THB","TJS","TMT","TND","TOP",
    "TRY","TTD","TVD","TWD","TZS","UAH","UGX","USD","UYU","UZS",
    "VES","VND","VUV","WST","XAF","XCD","XOF","XPF","YER","ZAR",
    "ZMW","ZWL"
]
# Top 5 más usados
TOP5 = ["NZD", "AUD", "USD", "EUR", "ARS"]

router = APIRouter(prefix="/payment_methods", tags=["Payment Methods"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1) Formulario HTML para agregar
@router.get("/new", response_class=HTMLResponse)
def new_payment_method_form(request: Request):
    # Orden: primero TOP5 con bandera, luego el resto alfabético
    otras_monedas = sorted([c for c in ALL_CURRENCIES if c not in TOP5])
    return templates.TemplateResponse(
        "payment_method_form.html",
        {"request": request, "otras_monedas": otras_monedas}
    )

# 2) Página HTML para editar
@router.get("/edit", response_class=HTMLResponse)
def edit_payment_methods(request: Request, db: Session = Depends(get_db)):
    methods = crud.get_payment_methods(db)
    return templates.TemplateResponse(
        "payment_method_edit.html",
        {"request": request, "payment_methods": methods}
    )

# 3) API JSON para crear
@router.post("/", response_model=schemas.PaymentMethodOut)
def create_payment_method(pm: schemas.PaymentMethodCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_payment_method(db, pm)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4) API JSON para listar
@router.get("/", response_model=List[schemas.PaymentMethodOut])
def list_payment_methods(db: Session = Depends(get_db)):
    return crud.get_payment_methods(db)

# 5) API DELETE
@router.delete("/id/{id}")
def delete_payment_method(id: int, db: Session = Depends(get_db)):
    try:
        if not crud.delete_payment_method_by_id(db, id):
            raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
        return {"message": "Eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 6) API JSON para actualizar
@router.put("/id/{id}", response_model=schemas.PaymentMethodOut)
def update_payment_method(id: int, pm_data: schemas.PaymentMethodCreate, db: Session = Depends(get_db)):
    try:
        updated = crud.update_payment_method_by_id(db, id, pm_data.name, pm_data.currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")
    return updated
