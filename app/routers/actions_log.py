from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.templates import templates
from app.crud.actions import get_actions

router = APIRouter(prefix="/actions", tags=["Actions Log"])


@router.get("/", response_class=HTMLResponse)
def actions_list(request: Request, db: Session = Depends(get_db)):
    logs = get_actions(db)
    return templates.TemplateResponse("actions_log.html", {"request": request, "logs": logs})

