from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from .. import models, schemas, crud
from .. database import get_db
from ..core.templates import templates

router = APIRouter(prefix="/compras", tags=["compras"])

@router.get("/new")
def form_compra_add(request: Request):
    """
    Renderiza el formulario HTML para registrar una nueva compra.
    """
    return templates.TemplateResponse("compra_add.html", {"request": request})

@router.post("/new", response_model=schemas.CompraOut)
def crear_compra(
    concepto: str = Form(...),
    fecha: datetime = Form(...),
    archivo: UploadFile = File(None),   # Opcional
    db: Session = Depends(get_db),
):
    """
    Crea una nueva compra.

    - Recibe: concepto (texto), fecha (datetime), y un archivo opcional (UploadFile).
    - Si se envía un archivo, lo guarda y asocia a la compra.
    - Devuelve la compra creada, incluyendo los datos del archivo asociado.
    - (Nota: Actualmente, la compra requiere un archivo. Para permitir compras sin archivo,
      hacer archivo_id nullable en el modelo y quitar la excepción.)
    """
    archivo_id = None
    archivo_obj = None

    # Si viene archivo, lo guarda y obtiene el id
    if archivo is not None:
        archivo_obj = crud.create_archivo(db, archivo)
        archivo_id = archivo_obj.id

    # Si no hay archivo, lanza error (opcional según tu lógica)
    if not archivo_id:
        raise HTTPException(status_code=400, detail="Se requiere archivo para la compra.")  # O quitar si aceptás null

    compra_create = schemas.CompraCreate(
        concepto=concepto,
        fecha=fecha,
        archivo_id=archivo_id
    )
    compra = crud.create_compra(db, compra_create)
    return compra

@router.get("/", response_model=list[schemas.CompraOut])
def listar_compras(db: Session = Depends(get_db)):
    """
    Devuelve una lista de todas las compras registradas, ordenadas por fecha descendente.

    - Incluye información del archivo asociado para cada compra.
    - Ideal para mostrar un listado general de compras.
    """
    compras = crud.get_compras(db)
    return compras

@router.get("/{compra_id}", response_model=schemas.CompraOut)
def obtener_compra(compra_id: int, db: Session = Depends(get_db)):
    """
    Devuelve una compra específica por su ID.

    - Si no existe, responde con error 404.
    - Incluye información del archivo asociado.
    """
    compra = db.query(models.Compra).filter(models.Compra.id == compra_id).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return compra
