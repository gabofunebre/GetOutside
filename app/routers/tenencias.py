# app/routers/tenencias.py

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.crud import get_tenencias_convertidas
from app.core.deps import get_db
from app.core.templates import templates
from app.core.currencies import FRANKFURTER_API_URL
from app.exceptions.dinero import ConversionMonedaFallida

router = APIRouter(prefix="/tenencias", tags=["Tenencias"])


@router.get("/", response_class=HTMLResponse)
def tenencias_overview(
    request: Request,
    target_currency: str = Query("NZD", min_length=3, max_length=3),
    db: Session = Depends(get_db),
):
    """
    Muestra las tenencias por método de pago,
    convertidos a la moneda `target_currency` usando Frankfurter API.
    """
    try:
        por_medio, total_converted, error_msg = get_tenencias_convertidas(
            db=db,
            target_currency=target_currency,
            frankfurter_base_url=FRANKFURTER_API_URL,
        )
    except ConversionMonedaFallida as e:
        por_medio = []
        total_converted = 0.0
        error_msg = str(e)

    return templates.TemplateResponse(
        "tenencias_overview.html",
        {
            "request": request,
            "target_currency": target_currency,
            "total": total_converted,
            "por_medio": por_medio,
            "error_msg": error_msg,
        },
    )
