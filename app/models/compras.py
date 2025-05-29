from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.db import Base


class Archivo(Base):
    __tablename__ = "archivos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False, unique=True)
    filepath = Column(String, nullable=False, unique=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    compras = relationship("Compra", back_populates="archivo")


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    concepto = Column(String, nullable=False)
    monto = Column(Float, nullable=False)

    archivo_id = Column(Integer, ForeignKey("archivos.id"), nullable=True)
    payment_method_id = Column(
        Integer, ForeignKey("payment_methods.id"), nullable=False
    )

    archivo = relationship("Archivo", back_populates="compras")
    payment_method = relationship("PaymentMethod")
