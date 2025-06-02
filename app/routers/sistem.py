from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/api/server-datetime")
def obtener_fecha_actual():
    """Devuelve la hora del sistema al frontend"""
    return {"datetime": datetime.now().isoformat()}
