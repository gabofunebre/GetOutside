from typing import Iterable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import RedirectResponse


class AuthRequiredMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        public_paths: Iterable[str] | None = None,
        public_prefixes: Iterable[str] | None = None,
    ):
        super().__init__(app)
        self.public_paths = set(public_paths or [])
        self.public_prefixes = tuple(public_prefixes or [])

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 🔐 Acceso seguro a session (evita crash si SessionMiddleware no está)
        session = request.session if "session" in request.scope else {}

        if path in self.public_paths or any(path.startswith(p) for p in self.public_prefixes):
            return await call_next(request)

        if session.get("user_id"):
            return await call_next(request)

        return RedirectResponse("/login")
