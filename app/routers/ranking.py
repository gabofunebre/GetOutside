# app/routers/ranking.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.templates import templates
from app.core.deps import get_db

router = APIRouter(prefix="/ranking", tags=["Ranking"])


@router.get("/", response_class=HTMLResponse)
def ranking_home(request: Request, db: Session = Depends(get_db)):
    """
    Página placeholder para ranking.
    Cuando esté lista la lógica, aquí la implementas.
    """
    # Puedes renderizar una plantilla o devolver un mensaje simple:
    return templates.TemplateResponse("ranking_placeholder.html", {"request": request})
