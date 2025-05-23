from pydantic import BaseModel, ConfigDict, constr
from datetime import datetime
from typing import List, Optional

# --- ESQUEMAS DE CATÁLOGOS ---

class CatalogoBase(BaseModel):
    """
    Campos base para gestión de catálogos PDF.
    """
    filename: str                       # Nombre del archivo

class CatalogoCreate(CatalogoBase):
    """
    Entrada para subir un nuevo catálogo.
    """
    pass

class Catalogo(BaseModel):
    """
    Salida de catálogo con metadatos.
    """
    id: int                             # ID autogenerado
    filepath: str                       # Ruta en servidor
    uploaded_at: datetime               # Fecha de subida

    # para poder usar .from_orm en Pydantic V2
    model_config = ConfigDict(from_attributes=True)

class CatalogoOut(BaseModel):
    id: int
    filename: str

    # para poder usar .from_orm en Pydantic V2
    model_config = ConfigDict(from_attributes=True)

class CatalogoUpdate(BaseModel):
    """
    Entrada para editar el nombre de un catálogo existente.
    """
    filename: str

# --- ESQUEMAS DE PRODUCTOS ---

class ProductoBase(BaseModel):
    """
    Campos base para crear o actualizar un producto.
    Incluye código único, descripción, catálogo asociado y precio.
    """
    codigo_getoutside: str               # Código único legible del producto
    descripcion: str                     # Descripción textual
    catalogo_id: int                     # FK a catálogo
    precio_venta: float                  # Precio de venta unitario

class ProductoCreate(ProductoBase):
    """
    Esquema para creación de producto.
    Añade campo de stock inicial.
    """
    stock_actual: int                    # Stock inicial disponible

class ProductoOut(BaseModel):
    """
    Respuesta de producto con todos los datos y su ID.
    """
    id: int
    codigo_getoutside: str
    descripcion: str
    precio_venta: float
    stock_actual: int
    catalogo_id: int
    catalogo: Optional[CatalogoOut] = None  # ← Relación con nombre del catálogo

    model_config = ConfigDict(from_attributes=True)

# --- ESQUEMAS DE DETALLES, PAGOS Y DESCUENTOS ---

class DetalleVentaIn(BaseModel):
    """
    Entrada de detalle de venta: referencia por ID de producto.
    """
    producto_id: int                     # ID del producto vendido
    cantidad: int                        # Cantidad vendida
    precio_unitario: float               # Precio aplicado por unidad

class DetalleVentaOut(DetalleVentaIn):
    """
    Esquema de salida para detalle de venta, con subtotal calculado.
    """
    subtotal: float                      # cantidad * precio_unitario

    # si alguna vez lo validas desde ORM
    model_config = ConfigDict(from_attributes=True)

class PagoCreate(BaseModel):
    """
    Entrada de pago: método y monto.
    """
    payment_method_id: int               # ID del medio de pago utilizado
    amount: float                        # Monto pagado

class PaymentMethodBase(BaseModel):
    """
    Campos base para crear o actualizar métodos de pago.
    """
    name: str                            # Nombre del medio (p.ej. "Tarjeta")

class PaymentMethodCreate(PaymentMethodBase):
    """
    Esquema para creación de método de pago, añade moneda ISO.
    """
    currency: constr(min_length=3, max_length=3)  # ISO 4217

class PaymentMethodOut(PaymentMethodBase):
    """
    Salida de método de pago con ID y moneda.
    """
    id: int                              # ID autogenerado
    currency: constr(min_length=3, max_length=3)

    model_config = ConfigDict(from_attributes=True)

class PagoOut(PagoCreate):
    """
    Salida de un pago, incluye detalle del medio de pago.
    """
    metodo: PaymentMethodOut             # Objeto anidado del medio

    model_config = ConfigDict(from_attributes=True)

class DescuentoCreate(BaseModel):
    """
    Entrada de descuento aplicado a la venta.
    """
    concepto: str                       # Descripción del descuento
    amount: float                       # Monto descontado

class DescuentoOut(DescuentoCreate):
    """
    Salida de descuento.
    """
    model_config = ConfigDict(from_attributes=True)

# --- ESQUEMAS DE VENTAS COMPLETAS ---

class VentaCreate(BaseModel):
    """
    Entrada para crear una venta con detalles, pagos y descuentos.
    """
    detalles: List[DetalleVentaIn]      # Lista de ítems vendidos
    pagos:    List[PagoCreate]          # Lista de pagos recibidos
    descuentos: Optional[List[DescuentoCreate]] = []  # Descuentos opcionales

class VentaOut(BaseModel):
    """
    Salida completa de una venta registrada.
    """
    id: int                             # ID de la venta
    fecha: datetime                    # Fecha y hora de la venta
    total: float                       # Total neto de la venta
    detalles: List[DetalleVentaOut]    # Detalles con subtotales
    pagos:    List[PagoOut]            # Pagos detallados
    descuentos: List[DescuentoOut]     # Descuentos aplicados

    model_config = ConfigDict(from_attributes=True)
