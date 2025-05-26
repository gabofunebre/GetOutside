# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
# Routers existentes...
from .routers import dashboard, productos, ventas, payment_methods, stock, ingresos, ranking, catalogos, movimientos_dinero
# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GetOutside Stock API")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Dashboard y subpáginas
app.include_router(dashboard.router)

# Routers
app.include_router(productos.router)
app.include_router(ventas.router)
app.include_router(payment_methods.router)
app.include_router(stock.router)
app.include_router(ingresos.router)
app.include_router(ranking.router)  # ← Asegúrate de tener esta línea
app.include_router(catalogos.router)
app.include_router(movimientos_dinero.router)

@app.get("/")
def read_root():
    return {"message": "GetOutside Stock API is running!"}
