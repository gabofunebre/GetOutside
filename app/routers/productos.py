# app/routers/productos.py

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.inventario import Producto, Catalogo
from app.schemas.producto import ProductoBase, ProductoCreate, ProductoOut
from app.crud.inventario import (
    get_producto,
    create_producto,
    agregar_stock,
    update_producto_completo,
)
from app.core.deps import get_db
from app.core.templates import templates

router = APIRouter(prefix="/productos", tags=["Productos"])

# === MODELO AUXILIAR para actualizaciones parciales ===


class StockUpdate(BaseModel):
    stock_agregado: int  # cantidad a sumar o restar al stock_actual


# === CREACIÓN DE PRODUCTOS ===


@router.post("/", response_model=ProductoOut)
def crear_producto(p: ProductoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo producto y lo devuelve"""
    return create_producto(db, p)


# === FORMULARIO HTML ===


@router.get("/new", response_class=HTMLResponse)
def new_product_form(request: Request, db: Session = Depends(get_db)):
    """Renderiza la vista para crear un nuevo producto"""
    catalogos = db.query(Catalogo).all()
    return templates.TemplateResponse(
        "product_form.html", {"request": request, "catalogos": catalogos}
    )


# === CONSULTA DE PRODUCTOS POR ID ===


@router.get("/id/{producto_id}", response_model=ProductoOut)
def read_producto_by_id(producto_id: int, db: Session = Depends(get_db)):
    """Devuelve un producto dado su ID"""
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod


# === ACTUALIZAR STOCK POR ID ===


@router.put("/id/{producto_id}/stock", response_model=ProductoOut)
def update_stock_by_id(
    producto_id: int, data: StockUpdate, db: Session = Depends(get_db)
):
    """
    Ajusta únicamente el stock de un producto.
    """
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return agregar_stock(db, prod, data.stock_agregado)


# === LISTADO DE PRODUCTOS COMPLETO ===


@router.get("/", response_model=list[ProductoOut])
def list_productos(db: Session = Depends(get_db)):
    """Devuelve todos los productos registrados"""
    return db.query(Producto).all()


# === VALIDACIÓN POR CÓDIGO (para frontend) ===


@router.get("", response_model=dict, include_in_schema=False)
def producto_existe_por_codigo(
    codigo: Optional[str] = None, db: Session = Depends(get_db)
):
    """Consulta si un producto existe por código. Devuelve 'exists' y datos mínimos si aplica"""
    if not codigo:
        raise HTTPException(status_code=400, detail="Código no proporcionado")

    prod = db.query(Producto).filter(Producto.codigo_getoutside == codigo).first()
    if not prod:
        return {"exists": False}

    return {
        "exists": True,
        "id": prod.id,
        "codigo_getoutside": prod.codigo_getoutside,
        "descripcion": prod.descripcion,
        "catalogo_id": prod.catalogo_id,
        "precio_venta": float(prod.precio_venta),
        "stock_actual": prod.stock_actual,
    }


# ====  ELIMINACIÓN POR ID ====


@router.delete("/id/{producto_id}")
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Elimina un producto por su ID si no tiene ventas asociadas.
    - Rechaza la eliminación si el producto ya fue vendido.
    """
    # Buscar el producto
    prod = db.query(Producto).filter(Producto.id == producto_id).first()

    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Verificar si tiene ventas asociadas (relación detalles_venta no vacía)
    if prod.detalles_venta:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar: producto con ventas registradas.",
        )

    # Eliminar si no fue vendido
    db.delete(prod)
    db.commit()

    return {"success": True, "message": "Producto eliminado correctamente"}


# === RENDER EDICION ===


@router.get("/edit", response_class=HTMLResponse)
def edit_productos_view(request: Request, db: Session = Depends(get_db)):
    """
    Vista HTML para la edición de productos.
    Renderiza una tabla interactiva con modal de edición.
    """
    return templates.TemplateResponse("product_edit.html", {"request": request})


# === EDICION POR ID CON VALIDACIÓN ===


@router.put("/id/{producto_id}", response_model=ProductoOut)
def actualizar_producto_completo(
    producto_id: int, data: ProductoCreate, db: Session = Depends(get_db)
):
    """
    Endpoint para actualizar todos los campos de un producto.
    - Usa lógica centralizada desde crud.py
    - Lanza HTTP 400 en errores de validación.
    """
    try:
        return update_producto_completo(db, producto_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
