# app/models.py
from sqlalchemy import (
    Column, Integer, String, DECIMAL, DateTime, Enum, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class TipoMov(enum.Enum):
    ENTRADA = "ENTRADA"
    SALIDA  = "SALIDA"

class Producto(Base):
    __tablename__ = "productos"

    id                = Column(Integer, primary_key=True, index=True)
    codigo_getoutside = Column(String, nullable=False, unique=True, index=True)
    descripcion       = Column(String, nullable=False)
    catalogo_id       = Column(Integer, ForeignKey("catalogos.id"), nullable=False)
    precio_venta      = Column(DECIMAL(12,2), nullable=False)
    stock_actual      = Column(Integer, nullable=False)

    catalogo = relationship("Catalogo")
    movimientos      = relationship("InventarioMovimiento", back_populates="producto")
    detalles_venta   = relationship("DetalleVenta", back_populates="producto")

class InventarioMovimiento(Base):
    __tablename__ = "inventario_movimientos"
    id                = Column(Integer, primary_key=True, index=True)
    codigo_getoutside = Column(String, ForeignKey("productos.codigo_getoutside"), nullable=False)
    fecha             = Column(DateTime, default=datetime.utcnow)
    tipo              = Column(Enum(TipoMov), nullable=False)
    cantidad          = Column(Integer, nullable=False)
    referencia        = Column(String)

    producto = relationship("Producto", back_populates="movimientos")

class Venta(Base):
    __tablename__ = "ventas"
    id      = Column(Integer, primary_key=True, index=True)
    fecha   = Column(DateTime, default=datetime.utcnow)
    total   = Column(DECIMAL(14,2), nullable=False)

    detalles   = relationship("DetalleVenta", back_populates="venta", cascade="all, delete")
    pagos      = relationship("VentaPago", back_populates="venta", cascade="all, delete")
    descuentos = relationship("Descuento", back_populates="venta", cascade="all, delete")

class Descuento(Base):
    __tablename__ = "descuentos"
    id         = Column(Integer, primary_key=True, index=True)
    venta_id   = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    concepto   = Column(String, nullable=False)
    amount     = Column(DECIMAL(14,2), nullable=False)

    venta = relationship("Venta", back_populates="descuentos")

class DetalleVenta(Base):
    __tablename__ = "venta_detalles"
    id                = Column(Integer, primary_key=True, index=True)
    venta_id          = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    codigo_getoutside = Column(String, ForeignKey("productos.codigo_getoutside"), nullable=False)
    cantidad          = Column(Integer, nullable=False)
    precio_unitario   = Column(DECIMAL(12,2), nullable=False)
    subtotal          = Column(DECIMAL(14,2), nullable=False)

    venta    = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String, unique=True, nullable=False)
    pagos = relationship("VentaPago", back_populates="metodo", cascade="all, delete")

class VentaPago(Base):
    __tablename__ = "venta_pagos"
    id                = Column(Integer, primary_key=True, index=True)
    venta_id          = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    amount            = Column(DECIMAL(14,2), nullable=False)

    venta  = relationship("Venta",         back_populates="pagos")
    metodo = relationship("PaymentMethod", back_populates="pagos")

    @property
    def metodo_str(self):
        return self.metodo.name if self.metodo else None

class Catalogo(Base):
    __tablename__ = "catalogos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, unique=True)
    filepath = Column(String, nullable=False, unique=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)