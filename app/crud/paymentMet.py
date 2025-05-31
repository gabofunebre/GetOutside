from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models import PaymentMethod, VentaPago
from app.schemas.pago import PaymentMethodCreate


def create_payment_method(db: Session, pm: PaymentMethodCreate) -> PaymentMethod:
    """Crea un nuevo medio de pago validando unicidad (case-insensitive)."""
    existente = (
        db.query(PaymentMethod)
        .filter(func.lower(PaymentMethod.name) == pm.name.lower())
        .first()
    )

    if existente:
        raise ValueError(f"Ya existe un medio de pago con el nombre '{pm.name}'.")

    pm_obj = PaymentMethod(name=pm.name, currency=pm.currency.upper())
    db.add(pm_obj)
    db.commit()
    db.refresh(pm_obj)
    return pm_obj


def get_payment_methods(db: Session) -> list[PaymentMethod]:
    """Recupera todos los métodos de pago registrados."""
    return db.query(PaymentMethod).all()


def delete_payment_method_by_id(db: Session, id: int) -> bool:
    """Elimina un método si no está referenciado en ventas."""
    usado = db.query(VentaPago).filter_by(payment_method_id=id).first()
    if usado:
        raise HTTPException(
            status_code=400,
            detail="Medio de pago en uso, no se puede eliminar. Pruebe con editar o crear uno nuevo"
        )

    pm = db.query(PaymentMethod).filter(PaymentMethod.id == id).first()
    if not pm:
        return False

    db.delete(pm)
    db.commit()
    return True


def update_payment_method_by_id(
    db: Session, id: int, new_name: str, new_currency: str
) -> PaymentMethod | None:
    """Actualiza nombre y moneda de un método de pago, validando unicidad."""
    pm = db.query(PaymentMethod).filter(PaymentMethod.id == id).first()
    if not pm:
        return None

    existente = (
        db.query(PaymentMethod)
        .filter(
            func.lower(PaymentMethod.name) == new_name.lower(), PaymentMethod.id != id
        )
        .first()
    )
    if existente:
        raise ValueError(f"Ya existe un medio de pago con el nombre '{new_name}'.")

    pm.name = new_name
    pm.currency = new_currency.upper()
    db.commit()
    db.refresh(pm)
    return pm
