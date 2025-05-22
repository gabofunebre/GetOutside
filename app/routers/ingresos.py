# app/routers/ingresos.py

import requests
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from .. import crud, database
from ..core.templates import templates

router = APIRouter(prefix="/ingresos", tags=["Ingresos"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
def ingresos_overview(
    request: Request,
    target_currency: str = Query("NZD", min_length=3, max_length=3),
    db: Session = Depends(get_db)
):
    """
    Muestra los ingresos por método de pago,
    convertidos a la moneda `target_currency` usando Frankfurter API.
    """
    data = crud.get_ingresos(db)
    por_medio = data["por_medio"]

    orig_currencies = {m["currency"] for m in por_medio if m["currency"] != target_currency}
    rates = {}
    error_msg = None

    try:
        if orig_currencies:
            params = {"base": target_currency, "symbols": ",".join(orig_currencies)}
            resp = requests.get("https://api.frankfurter.app/latest", params=params, timeout=5)
            resp.raise_for_status()
            rates = resp.json().get("rates", {})
    except Exception:
        rates = {}
        error_msg = "No fue posible obtener los tipos de cambio. Se muestran solo los valores en moneda original."

    total_converted = 0.0
    for m in por_medio:
        amt = m["amount"]
        if m["currency"] == target_currency:
            m["converted"] = round(amt, 2)
            total_converted += m["converted"]
        else:
            rate = rates.get(m["currency"])
            if rate:
                m["converted"] = round(amt / rate, 2)
                total_converted += m["converted"]
            else:
                m["converted"] = None

    return templates.TemplateResponse(
        "ingresos_overview.html",
        {
            "request": request,
            "target_currency": target_currency,
            "total": total_converted,
            "por_medio": por_medio,
            "error_msg": error_msg
        }
    )