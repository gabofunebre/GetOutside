from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.schemas import MovimientoDineroCreate
from app.models import TipoMovimientoDinero


from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/movimientos-dinero", response_class=HTMLResponse)
def ver_movimientos_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("movimientos_dinero.html", {"request": request})

@router.get("/api/movimientos-dinero")
def listar_movimientos_dinero(db: Session = Depends(get_db)):
    movimientos = crud.get_movimientos_dinero(db)
    return [m.to_dict() for m in movimientos]  # necesitas agregar este método o usar un esquemafrom fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MovimientoDinero
from app.schemas import MovimientoDineroOut
from app import crud

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

# Vista HTML completa de movimientos (ordenable)
@router.get("/movimientos-dinero", response_class=HTMLResponse)
def ver_movimientos_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("movimientos_dinero.html", {"request": request})

# API JSON: últimos N movimientos, ordenados por fecha
@router.get("/api/movimientos-dinero", response_model=list[MovimientoDineroOut])
def listar_movimientos_dinero(limit: int = 30, db: Session = Depends(get_db)):
    movimientos = (
        db.query(MovimientoDinero)
        .order_by(MovimientoDinero.fecha.desc())
        .limit(limit)
        .all()
    )
    return movimientos

@router.post("/api/movimientos-dinero", status_code=201)
def crear_movimiento_dinero_api(
    movimiento: MovimientoDineroCreate,
    db: Session = Depends(get_db)
):
    nuevo = crud.crear_movimiento_dinero(
        db=db,
        tipo=movimiento.tipo,
        fecha=movimiento.fecha,
        concepto=movimiento.concepto,
        importe=movimiento.importe,
        metodo_pago_id=movimiento.payment_method_id
    )
    return JSONResponse(content={"id": nuevo.id}, status_code=status.HTTP_201_CREATED)