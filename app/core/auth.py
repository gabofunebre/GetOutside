
from typing import Iterable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import RedirectResponse


class AuthRequiredMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure user is authenticated for protected routes."""


    def __init__(self, app, public_paths: Iterable[str] | None = None,
                 public_prefixes: Iterable[str] | None = None):
        super().__init__(app)
        self.public_paths = set(public_paths or [])
        self.public_prefixes = tuple(public_prefixes or [])

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow access to explicitly whitelisted paths
        if path in self.public_paths:
            return await call_next(request)

        # Allow access to paths that share allowed prefixes (e.g. static files)
        if any(path.startswith(prefix) for prefix in self.public_prefixes):
            return await call_next(request)

        if request.session.get("user_id"):
            return await call_next(request)
        return RedirectResponse("/login")
