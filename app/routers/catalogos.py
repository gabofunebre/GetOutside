# app/routers/catalogos.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from .. import database, models, schemas, crud
from ..core.templates import templates

router = APIRouter(prefix="/catalogos", tags=["Catálogos"])

# === Dependencia para obtener la sesión de base de datos ===
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === 1) Vista HTML con lista de catálogos ===
@router.get("/", response_class=HTMLResponse)
def catalogos_html(request: Request, db: Session = Depends(get_db)):
    """Vista HTML con links a catálogos PDF"""
    catalogos = db.query(models.Catalogo).order_by(models.Catalogo.uploaded_at.desc()).all()
    return templates.TemplateResponse("catalogos.html", {"request": request, "catalogos": catalogos})

# === 2) Formulario para subir un nuevo catálogo ===
@router.get("/new", response_class=HTMLResponse)
def new_catalogo_form(request: Request):
    """Renderiza la página para subir un nuevo catálogo"""
    return templates.TemplateResponse("catalogo_upload.html", {"request": request})

# === 3) Subida de archivo PDF como catálogo ===
@router.post("/", status_code=303)
async def upload_catalogo(
    file: UploadFile = File(..., media_type="application/pdf"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Valida y guarda un archivo PDF como nuevo catálogo"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos PDF")
    try:
        crud.create_catalogo(db, file)
        return RedirectResponse(url="/catalogos", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse(
            "catalogo_upload.html",
            {"request": request, "error": str(e)},
            status_code=400
        )

# === 4) Descarga de catálogo PDF por ID ===
@router.get("/download/{catalogo_id}")
def download_catalogo(catalogo_id: int, db: Session = Depends(get_db)):
    """Devuelve el PDF del catálogo solicitado"""
    catalogo = crud.get_catalogo(db, catalogo_id)
    if not catalogo:
        raise HTTPException(status_code=404, detail="Catálogo no encontrado")
    return FileResponse(
        path=catalogo.filepath,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{catalogo.filename}"'}
    )

# === 5) API JSON para frontend ===
@router.get("/api", response_model=list[schemas.CatalogoOut])
def catalogos_json(db: Session = Depends(get_db)):
    """
    Endpoint JSON para el frontend.
    Devuelve todos los catálogos con ID y filename.
    """
    return db.query(models.Catalogo).all()
