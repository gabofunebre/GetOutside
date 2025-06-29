from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from app.core.db import Base, engine


def _ensure_foto_column():
    """Add foto_filename column if it's missing (simple auto-migration)."""
    inspector = inspect(engine)
    cols = [c["name"] for c in inspector.get_columns("productos")]
    if "foto_filename" not in cols:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE productos ADD COLUMN foto_filename VARCHAR"))
            conn.commit()

# Routers existentes
from .routers import (
    dashboard,
    productos,
    ventas,
    payment_methods,
    stock,
    tenencias,
    ranking,
    catalogos,
    movimientos_dinero,
    compras,
    sistem,
)

# Crear tablas en base de datos
_ensure_foto_column()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GetOutside Stock API")

# Archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(dashboard.router)
app.include_router(productos.router)
app.include_router(ventas.router)
app.include_router(payment_methods.router)
app.include_router(stock.router)
app.include_router(ranking.router)
app.include_router(catalogos.router)
app.include_router(movimientos_dinero.router)
app.include_router(compras.router)
app.include_router(tenencias.router)
app.include_router(sistem.router)

@app.get("/")
def read_root():
    return {"message": "GetOutside Stock API is running!"}
