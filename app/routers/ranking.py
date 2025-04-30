# app/routers/ranking.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import database, crud, models

router = APIRouter(prefix="/ranking", tags=["Ranking"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
def ranking_filter(request: Request, db: Session = Depends(get_db)):
    # Distinct lists for selects
    tipos = [r[0] for r in db.query(models.Producto.tipo).distinct().all() if r[0]]
    procesos = [r[0] for r in db.query(models.Producto.proceso_aplicado).distinct().all() if r[0]]
    disenos = [r[0] for r in db.query(models.Producto.diseno_aplicado).distinct().all() if r[0]]
    return templates.TemplateResponse(
        "ranking_filter.html",
        {
            "request": request,
            "tipos": tipos,
            "procesos": procesos,
            "disenos": disenos
        }
    )

@router.get("/list", response_class=HTMLResponse)
def ranking_list(
    request: Request,
    start: str | None = Query(None),
    end:   str | None = Query(None),
    tipo:               str | None = Query(None),
    proceso_aplicado:   str | None = Query(None),
    diseno_aplicado:    str | None = Query(None),
    db: Session = Depends(get_db)
):
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt   = datetime.fromisoformat(end)   if end   else None
    results = crud.get_product_ranking(
        db,
        start=start_dt,
        end=end_dt,
        tipo=tipo,
        proceso_aplicado=proceso_aplicado,
        diseno_aplicado=diseno_aplicado
    )
    return templates.TemplateResponse(
        "ranking_list.html",
        {"request": request, "results": results}
    )
