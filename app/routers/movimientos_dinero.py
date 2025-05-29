from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from app.crud.dinero import listar_movimientos, crear_y_guardar_movimiento
from app.schemas.dinero import MovimientoDineroCreate, MovimientoDineroOut
from app.models.dinero import TipoMovimientoDinero, MovimientoDinero
from app.core.deps import get_db
from app.core.templates import templates

from app.core.config import DEFAULT_MOVIMIENTOS_LIMIT

router = APIRouter()


# Vista HTML completa de movimientos (ordenable)
@router.get("/movimientos-dinero", response_class=HTMLResponse)
def ver_movimientos_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("movimientos_dinero.html", {"request": request})


# API JSON: últimos N movimientos, ordenados por fecha
@router.get("/api/movimientos-dinero", response_model=list[MovimientoDineroOut])
def listar_movimientos_dinero(
    limit: int = DEFAULT_MOVIMIENTOS_LIMIT,  # 👈 Usás la constante como valor por defecto
    db: Session = Depends(get_db),
):
    return listar_movimientos(db, limit=limit)


@router.post("/api/movimientos-dinero", status_code=201)
def crear_movimiento_dinero_api(
    movimiento: MovimientoDineroCreate, db: Session = Depends(get_db)
):
    nuevo = crear_y_guardar_movimiento(
        db=db,
        tipo=movimiento.tipo,
        fecha=movimiento.fecha,
        concepto=movimiento.concepto,
        importe=movimiento.importe,
        metodo_pago_id=movimiento.payment_method_id,
    )
    return JSONResponse(content={"id": nuevo.id}, status_code=status.HTTP_201_CREATED)
