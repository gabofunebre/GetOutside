from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

from app.models import Producto, InventarioMovimiento, Catalogo, TipoMov
from app.schemas.producto import ProductoCreate
from app.core.config import CATALOGOS_DIR

# === PRODUCTOS ===


def get_producto(db: Session, producto_id: int) -> Optional[Producto]:
    """Devuelve un Producto por su ID."""
    return db.query(Producto).filter(Producto.id == producto_id).first()


def create_producto(db: Session, p: ProductoCreate) -> Producto:
    """Crea y devuelve un nuevo Producto."""
    db_p = Producto(**p.dict())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p

def update_producto_completo(
    db: Session, producto_id: int, data: ProductoCreate
) -> Producto:
    """
    Actualiza completamente un producto existente:
    - Cambia código, descripción, precio, stock y catálogo.
    - Valida que el nuevo código no esté en uso por otro producto.
    """
    # Buscar producto por ID
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise ValueError("Producto no encontrado")

    # Validar unicidad del código GetOutside, excluyendo el mismo producto
    duplicado = (
        db.query(Producto)
        .filter(
            Producto.codigo_getoutside == data.codigo_getoutside,
            Producto.id != producto_id,
        )
        .first()
    )
    if duplicado:
        raise ValueError("Código GetOutside ya en uso por otro producto.")

    # Asignar nuevos valores
    prod.codigo_getoutside = data.codigo_getoutside
    prod.descripcion = data.descripcion
    prod.precio_venta = data.precio_venta
    prod.stock_actual = data.stock_actual
    prod.catalogo_id = data.catalogo_id

    # Guardar cambios
    db.commit()
    db.refresh(prod)
    return prod


# === STOCK / INVENTARIO ===


def update_stock(
    db: Session, producto_id: int, delta: int, referencia: str
) -> Producto:
    """Crea un movimiento de inventario y ajusta el stock del Producto."""
    prod = get_producto(db, producto_id)
    prod.stock_actual += delta
    mov = InventarioMovimiento(
        producto_id=producto_id,
        tipo=TipoMov.ENTRADA if delta > 0 else TipoMov.SALIDA,
        cantidad=abs(delta),
        referencia=referencia,
    )
    db.add(mov)
    db.commit()
    return prod


# === CATÁLOGOS ===


def create_catalogo(db: Session, file: UploadFile) -> Catalogo:
    """Guarda un archivo de catálogo y crea el registro en base de datos."""
    os.makedirs(CATALOGOS_DIR, exist_ok=True)
    dest_path = os.path.join(CATALOGOS_DIR, file.filename)
    print("DEBUG - Voy a guardar en:", dest_path)
    with open(dest_path, "wb") as out:
        out.write(file.file.read())
    db_obj = Catalogo(filename=file.filename, filepath=dest_path)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_catalogos(db: Session) -> list[Catalogo]:
    """Recupera todos los catálogos ordenados por fecha descendente."""
    return db.query(Catalogo).order_by(Catalogo.uploaded_at.desc()).all()


def get_catalogo(db: Session, catalogo_id: int) -> Optional[Catalogo]:
    """Recupera un catálogo por su ID."""
    return db.query(Catalogo).filter(Catalogo.id == catalogo_id).first()


def update_catalogo(db: Session, catalogo_id: int, nuevo_nombre: str) -> Catalogo:
    """Actualiza el nombre de un catálogo existente."""
    catalogo = get_catalogo(db, catalogo_id)
    if not catalogo:
        raise ValueError("Catálogo no encontrado")

    # Verifica unicidad del nuevo nombre
    duplicado = (
        db.query(Catalogo)
        .filter(
            func.lower(Catalogo.filename) == nuevo_nombre.lower(),
            Catalogo.id != catalogo_id,
        )
        .first()
    )
    if duplicado:
        raise ValueError("Ya existe un catálogo con ese nombre.")

    catalogo.filename = nuevo_nombre
    db.commit()
    db.refresh(catalogo)
    return catalogo


def delete_catalogo(db: Session, catalogo_id: int) -> bool:
    """Elimina un catálogo si no está vinculado a productos."""
    catalogo = get_catalogo(db, catalogo_id)
    if not catalogo:
        raise ValueError("Catálogo no encontrado")

    en_uso = db.query(Producto).filter_by(catalogo_id=catalogo.id).first()
    if en_uso:
        raise ValueError("Catálogo en uso por productos.")

    db.delete(catalogo)
    db.commit()
    return True
