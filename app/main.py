from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.db import Base, engine

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
