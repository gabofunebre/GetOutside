from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from app.core.db import Base, engine, SessionLocal
from app.crud import users as crud_users
from app.models.user import UserRole
from app.core import config
import os


def _ensure_extra_columns():
    """Add optional columns if they're missing (simple auto-migration)."""
    inspector = inspect(engine)
    cols = [c["name"] for c in inspector.get_columns("productos")]
    with engine.connect() as conn:
        if "foto_filename" not in cols:
            conn.execute(text("ALTER TABLE productos ADD COLUMN foto_filename VARCHAR"))
        if "costo_produccion" not in cols:
            conn.execute(
                text("ALTER TABLE productos ADD COLUMN costo_produccion DECIMAL(12,2)")
            )
        conn.commit()

    # Optional columns for users
    cols = [c["name"] for c in inspector.get_columns("users")]
    with engine.connect() as conn:
        if "first_name" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR"))
        if "last_name" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR"))
        if "oauth_provider" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR"))
        if "foto_filename" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN foto_filename VARCHAR"))
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
    users,
)

# Crear tablas en base de datos
Base.metadata.create_all(bind=engine)
_ensure_extra_columns()


def _ensure_admin_user():
    """Create default admin user if none exists."""
    with SessionLocal() as db:
        if not crud_users.get_user_by_email(db, config.ADMIN_EMAIL):
            crud_users.create_user(
                db,
                email=config.ADMIN_EMAIL,
                password="admin",
                role=UserRole.ADMIN,
            )


_ensure_admin_user()

app = FastAPI(title="GetOutside Stock API")
# Expira la sesión después de 10 minutos de inactividad
SESSION_TIMEOUT = 10 * 60  # 10 minutos en segundos
@app.middleware("http")
async def require_login(request: Request, call_next):
    public_paths = {
        "/login",
        "/register",
        "/auth/google",
        "/auth/google/callback",
        "/openapi.json",
    }
    if request.url.path.startswith("/static") or request.url.path.startswith("/docs"):
        return await call_next(request)
    if request.url.path in public_paths:
        return await call_next(request)
    if not request.session.get("user_id"):
        return RedirectResponse("/login")
    return await call_next(request)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "secret"),
    max_age=SESSION_TIMEOUT,
)


@app.middleware("http")
async def require_login(request: Request, call_next):
    public_paths = {
        "/login",
        "/register",
        "/auth/google",
        "/auth/google/callback",
        "/openapi.json",
    }
    if request.url.path.startswith("/static") or request.url.path.startswith("/docs"):
        return await call_next(request)
    if request.url.path in public_paths:
        return await call_next(request)
    if not request.session.get("user_id"):
        return RedirectResponse("/login")
    return await call_next(request)

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
app.include_router(users.router)


@app.get("/")
def root(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")
