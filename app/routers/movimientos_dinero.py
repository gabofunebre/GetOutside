from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Depends, status, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from app.crud.dinero import (
    listar_movimientos,
    crear_y_guardar_movimiento,
    get_movimiento_by_id,
    filtrar_movimientos,
)
from app.schemas.dinero import MovimientoDineroCreate, MovimientoDineroOut
from app.models.dinero import TipoMovimientoDinero, MovimientoDinero
from app.core.deps import get_db
from app.core.templates import templates
from app.crud.actions import log_action

from app.core.config import DEFAULT_MOVIMIENTOS_LIMIT

router = APIRouter()


# Vista HTML completa de movimientos (ordenable)
@router.get("/movimientos-dinero", response_class=HTMLResponse)
def ver_movimientos_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("movimientos_dinero.html", {"request": request})


# API JSON: últimos N movimientos, ordenados por fecha
@router.get("/api/movimientos-dinero", response_model=list[MovimientoDineroOut])
def listar_movimientos_dinero(
    limit: int = DEFAULT_MOVIMIENTOS_LIMIT,
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    tipo: Optional[TipoMovimientoDinero] = Query(None),
    ventas: bool = False,
    concepto: Optional[str] = None,
    db: Session = Depends(get_db),
):
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None

    if ventas:
        concepto = "V#"

    if any([start_dt, end_dt, tipo, concepto]):
        return filtrar_movimientos(
            db=db,

            limit=None,

            start=start_dt,
            end=end_dt,
            tipo=tipo,
            concepto=concepto,
        )
    return listar_movimientos(db, limit=limit)


@router.post("/api/movimientos-dinero", status_code=201)
def crear_movimiento_dinero_api(
    movimiento: MovimientoDineroCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    nuevo = crear_y_guardar_movimiento(
        db=db,
        tipo=movimiento.tipo,
        fecha=movimiento.fecha,
        concepto=movimiento.concepto,
        importe=movimiento.importe,
        metodo_pago_id=movimiento.payment_method_id,
    )
    user_id = request.session.get("user_id")
    if user_id:
        log_action(
            db,
            user_id=user_id,
            action="MOVIMIENTO_DINERO",
            entity_type="MOVIMIENTO",
            entity_id=nuevo.id,
            detail=f"Movimiento {nuevo.tipo.value} #{nuevo.id}",
        )
    return JSONResponse(content={"id": nuevo.id}, status_code=status.HTTP_201_CREATED)

@router.get("/movimiento/{movimiento_id}", response_class=HTMLResponse)
def ver_movimiento_detalle(request: Request, movimiento_id: int, db: Session = Depends(get_db)):
    try:
        movimiento = get_movimiento_by_id(db, movimiento_id)
    except MovimientoNoRegistrado as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "mensaje": str(e)},
            status_code=404,
        )
@router.get("/api/movimiento/{movimiento_id}", response_model=MovimientoDineroOut)
def obtener_movimiento_api(movimiento_id: int, db: Session = Depends(get_db)):
    movimiento = get_movimiento_by_id(db, movimiento_id)
    return movimiento