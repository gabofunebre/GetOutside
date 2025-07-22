from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse


class AuthRequiredMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure user is authenticated for protected routes."""

    def __init__(self, app, public_paths=None):
        super().__init__(app)
        if public_paths is None:
            public_paths = []
        self.public_paths = public_paths

    async def dispatch(self, request, call_next):
        path = request.url.path
        if any(path.startswith(p) for p in self.public_paths):
            return await call_next(request)
        if request.session.get("user_id"):
            return await call_next(request)
        return RedirectResponse("/login")
