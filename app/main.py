import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from starlette.middleware.sessions import SessionMiddleware

from app.core.auth import AuthRequiredMiddleware
from app.core.db import Base, engine, SessionLocal
from app.core import config
from app.crud import users as crud_users
from app.models.user import UserRole

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear admin si no existe
def _ensure_admin_user():
    with SessionLocal() as db:
        if not crud_users.get_user_by_email(db, config.ADMIN_EMAIL):
            crud_users.create_user(
                db,
                email=config.ADMIN_EMAIL,
                password="admin",
                role=UserRole.ADMIN,
            )

_ensure_admin_user()

# Crear app
app = FastAPI(title="GetOutside Stock API")

SESSION_TIMEOUT = 10 * 60  # 10 minutos

# Middleware de autenticación
app.add_middleware(
    AuthRequiredMiddleware,
    public_paths=[
        "/login",
        "/register",
        "/auth/google",
        "/auth/google/callback",
        "/",
    ],
    public_prefixes=["/static"],
)

# Middleware de sesión
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    max_age=SESSION_TIMEOUT,
    same_site="lax",
    https_only=True,
    session_cookie="session"
)

# Archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
from .routers import (
    dashboard, productos, ventas, payment_methods, stock, tenencias,
    ranking, catalogos, movimientos_dinero, compras, sistem, users, actions_log
)

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
app.include_router(actions_log.router)

# Redirección raíz
@app.get("/")
def root(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")

