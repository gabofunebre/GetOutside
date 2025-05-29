from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base
from app.models.enums import TipoMovimientoDinero
from app.models.ventas import PaymentMethod


class MovimientoDinero(Base):
    __tablename__ = "movimientos_dinero"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    concepto = Column(String, nullable=False)
    importe = Column(DECIMAL(14, 2), nullable=False)
    tipo = Column(Enum(TipoMovimientoDinero), nullable=False)
    payment_method_id = Column(
        Integer, ForeignKey("payment_methods.id"), nullable=False
    )

    metodo_pago = relationship("PaymentMethod", backref="movimientos_dinero")

class TenenciaAcumulada(Base):
    __tablename__ = "tenencias_acumuladas"

    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), primary_key=True)
    importe_acumulado = Column(Float, nullable=False)
    fecha_corte = Column(DateTime, nullable=False)

    metodo_pago = relationship("PaymentMethod", back_populates="tenencia_acumulada", lazy="joined")