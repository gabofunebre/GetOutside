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
    # Obtener totales originales
    data = crud.get_ingresos(db)
    por_medio = data["por_medio"]

    # Preparar lista de monedas origen (excluyendo la target)
    orig_currencies = {m["currency"] for m in por_medio if m["currency"] != target_currency}
    rates = {}
    if orig_currencies:
        # Llamada a Frankfurter: base=target_currency, symbols=origen1,origen2,...
        params = {"base": target_currency, "symbols": ",".join(orig_currencies)}
        resp = requests.get("https://api.frankfurter.app/latest", params=params)
        resp.raise_for_status()
        rates = resp.json().get("rates", {})

    # Convertir montos y calcular total convertido
    total_converted = 0.0
    for m in por_medio:
        amt = m["amount"]
        if m["currency"] == target_currency:
            m["converted"] = round(amt, 2)
        else:
            rate = rates.get(m["currency"])
            m["converted"] = round(amt / rate, 2) if rate else None
        total_converted += m["converted"] or 0.0

    return templates.TemplateResponse(
        "ingresos_overview.html",
        {
            "request": request,
            "target_currency": target_currency,
            "total": total_converted,
            "por_medio": por_medio
        }
    )
