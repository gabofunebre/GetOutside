import os
from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload

from app.models.enums import TipoMovimientoDinero
from app.models import Archivo, Compra
from app.schemas.compra import CompraCreate
from app.core.config import ARCHIVOS_DIR
from .dinero import crear_y_guardar_movimiento


def create_archivo(db: Session, file: UploadFile) -> Archivo:
    """Guarda un archivo en disco y crea el registro correspondiente."""
    os.makedirs(ARCHIVOS_DIR, exist_ok=True)
    dest_path = os.path.join(ARCHIVOS_DIR, file.filename)
    with open(dest_path, "wb") as out:
        out.write(file.file.read())

    db_obj = Archivo(filename=file.filename, filepath=dest_path)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_archivos(db: Session) -> list[Archivo]:
    """Recupera todos los archivos ordenados por fecha de subida."""
    return db.query(Archivo).order_by(Archivo.uploaded_at.desc()).all()


def create_compra(db: Session, c: CompraCreate) -> Compra:
    """Registra una nueva compra."""
    db_obj = Compra(**c.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_compras(db: Session) -> list[Compra]:
    """Recupera todas las compras, con método de pago y archivo relacionados."""
    return (
        db.query(Compra)
        .options(joinedload(Compra.payment_method), joinedload(Compra.archivo))
        .order_by(Compra.fecha.desc())
        .all()
    )


def get_compra_by_id(db: Session, compra_id: int) -> Compra | None:
    return db.query(Compra).filter(Compra.id == compra_id).first()


def registrar_egreso_por_compra(db: Session, compra: Compra) -> None:
    movimiento = crear_y_guardar_movimiento(
        db=db,
        tipo=TipoMovimientoDinero.EGRESO,
        fecha=compra.fecha,
        concepto=f"Egreso por compra #{compra.id}",
        importe=compra.monto,
        metodo_pago_id=compra.payment_method_id,
    )

def crear_compra_completa(
    db: Session, compra_data: CompraCreate, archivo: UploadFile | None = None
) -> Compra:
    archivo_id = None

    if archivo is not None:
        archivo_obj = create_archivo(db, archivo)
        archivo_id = archivo_obj.id

    compra_data.archivo_id = archivo_id
    compra = create_compra(db, compra_data)

    registrar_egreso_por_compra(db, compra)

    return compra
