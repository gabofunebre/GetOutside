from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    total = Column(DECIMAL(14, 2), nullable=False)

    detalles = relationship(
        "DetalleVenta", back_populates="venta", cascade="all, delete"
    )
    pagos = relationship("VentaPago", back_populates="venta", cascade="all, delete")
    descuentos = relationship(
        "Descuento", back_populates="venta", cascade="all, delete"
    )
    vueltos = relationship("Vuelto", back_populates="venta", cascade="all, delete")


class DetalleVenta(Base):
    __tablename__ = "venta_detalles"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(DECIMAL(12, 2), nullable=False)
    subtotal = Column(DECIMAL(14, 2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")


class Descuento(Base):
    __tablename__ = "descuentos"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    concepto = Column(String, nullable=False)
    amount = Column(DECIMAL(14, 2), nullable=False)

    venta = relationship("Venta", back_populates="descuentos")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    currency = Column(String(3), nullable=False)

    pagos = relationship("VentaPago", back_populates="metodo", cascade="all, delete")
    tenencia_acumulada = relationship("TenenciaAcumulada", back_populates="metodo_pago", uselist=False)


class VentaPago(Base):
    __tablename__ = "venta_pagos"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    payment_method_id = Column(
        Integer, ForeignKey("payment_methods.id"), nullable=False
    )
    amount = Column(DECIMAL(14, 2), nullable=False)

    venta = relationship("Venta", back_populates="pagos")
    metodo = relationship("PaymentMethod", back_populates="pagos")

    @property
    def metodo_str(self):
        return self.metodo.name if self.metodo else None


class Vuelto(Base):
    __tablename__ = "vueltos"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    amount = Column(DECIMAL(14, 2), nullable=False)

    venta = relationship("Venta", back_populates="vueltos")
    metodo = relationship("PaymentMethod")
