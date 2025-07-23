from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.schemas.compra import CompraCreate, CompraOut
from app.crud import compras
from app.core.templates import templates
from app.core.deps import get_db

router = APIRouter(prefix="/compras", tags=["Compras"])


# =======================================================
# 1. Formulario HTML para registrar una nueva compra
# =======================================================
@router.get("/new")
def form_compra_add(request: Request):
    return templates.TemplateResponse("compra_add.html", {"request": request})


# =======================================================================
# 2. Registro de una nueva compra, con carga opcional de archivo asociado
#    - También registra un movimiento de egreso vinculado a esa compra
# =======================================================================
from fastapi import status
from app.crud.actions import log_action

@router.post("/new", response_model=CompraOut)
def crear_compra(
    request: Request,
    concepto: str = Form(...),
    fecha: datetime = Form(...),
    monto: float = Form(...),
    payment_method_id: int = Form(...),
    archivo: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    try:
        compra_data = CompraCreate(
            concepto=concepto,
            fecha=fecha,
            monto=monto,
            payment_method_id=payment_method_id
        )

        compra = compras.crear_compra_completa(db, compra_data, archivo)
        user_id = request.session.get("user_id")
        if user_id:
            log_action(
                db,
                user_id=user_id,
                action="CREAR_COMPRA",
                entity_type="COMPRA",
                entity_id=compra.id,
                detail=f"Compra #{compra.id} registrada",
            )
        return compra

    except ValueError as e:
        # Error por datos inválidos
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        # Error inesperado: loguearlo y devolver genérico
        # log.error("Error inesperado al crear compra", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al registrar la compra.")



# =======================================================
# 3. Listado de compras con sus archivos y métodos de pago
# =======================================================
@router.get("/", response_model=list[CompraOut])
def listar_compras(db: Session = Depends(get_db)):
    return compras.get_compras(db)


# ===========================================
# 4. Obtener detalle de una compra por su ID
# ===========================================
@router.get("/{compra_id}", response_model=CompraOut)
def obtener_compra(compra_id: int, db: Session = Depends(get_db)):
    compra = compras.get_compra_by_id(db, compra_id)
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return compra

# =====================================================
# 4. Renderiza con los  detalle de una compra por su ID
# ====================================================
@router.get("/detalle/{compra_id}")
def vista_detalle_compra(request: Request, compra_id: int):
    return templates.TemplateResponse("compra_detalle.html", {
        "request": request,
        "compra_id": compra_id
    })

