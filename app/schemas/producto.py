from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.catalogo import CatalogoOut


class ProductoBase(BaseModel):
    """
    Campos base para crear o actualizar un producto.
    Incluye código único, descripción, catálogo asociado y precio.
    """

    codigo_getoutside: str  # Código único legible del producto
    descripcion: str  # Descripción textual
    catalogo_id: Optional[int] = None  # FK a catálogo
    precio_venta: float  # Precio de venta unitario
    costo_produccion: Optional[float] = None  # Costo de producción


class ProductoCreate(ProductoBase):
    """
    Esquema para creación de producto.
    Añade campo de stock inicial.
    """

    stock_actual: int  # Stock inicial disponible
    foto_filename: Optional[str] = None


class ProductoOut(BaseModel):
    """
    Respuesta de producto con todos los datos y su ID.
    """

    id: int
    codigo_getoutside: str
    descripcion: str
    precio_venta: float
    costo_produccion: Optional[float] = None
    stock_actual: int
    catalogo_id: Optional[int]
    catalogo: Optional[CatalogoOut] = None
    foto_filename: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
