# app/routers/payment_methods.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database

router = APIRouter(prefix="/payment_methods", tags=["Payment Methods"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1) Formulario HTML (GET /payment_methods/new)
@router.get("/new", response_class=HTMLResponse)
def new_payment_method_form(request: Request):
    return templates.TemplateResponse(
        "payment_method_form.html",
        {"request": request}
    )

# 2) API JSON para crear métodos (POST /payment_methods)
@router.post("/", response_model=schemas.PaymentMethodOut)
def create_payment_method(pm: schemas.PaymentMethodCreate, db: Session = Depends(get_db)):
    # opcional: podrías chequear duplicados aquí y lanzar HTTPException(400)
    return crud.create_payment_method(db, pm)

# 3) API JSON para listar (GET /payment_methods)
@router.get("/", response_model=List[schemas.PaymentMethodOut])
def list_payment_methods(db: Session = Depends(get_db)):
    return crud.get_payment_methods(db)
