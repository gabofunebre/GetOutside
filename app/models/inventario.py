
#app/models/inventario.py
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Enum as PgEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base
from app.models.enums import TipoMov

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_getoutside = Column(String, nullable=False, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    catalogo_id = Column(Integer, ForeignKey("catalogos.id"), nullable=False)
    precio_venta = Column(DECIMAL(12, 2), nullable=False)
    stock_actual = Column(Integer, nullable=False)

    catalogo = relationship("Catalogo")
    movimientos = relationship("InventarioMovimiento", back_populates="producto")
    detalles_venta = relationship("DetalleVenta", back_populates="producto")


class InventarioMovimiento(Base):
    __tablename__ = "inventario_movimientos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    #tipo = Column(String, nullable=False)  # TipoMov se manejará por enums.py
    tipo = Column(PgEnum(TipoMov, name="tipomov", native_enum=True), nullable=False)
    cantidad = Column(Integer, nullable=False)
    referencia = Column(String)

    producto = relationship("Producto", back_populates="movimientos")


class Catalogo(Base):
    __tablename__ = "catalogos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, unique=True)
    filepath = Column(String, nullable=False, unique=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
