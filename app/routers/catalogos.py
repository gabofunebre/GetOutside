# app/routers/catalogos.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from ..core.templates import templates
from .. import crud, deps

router = APIRouter(
    prefix="/catalogos",
    tags=["Catalogos"]
)

# === 1) Lista de catálogos ===
@router.get("/", response_class=HTMLResponse)
def list_catalogos(request: Request, db: Session = Depends(deps.get_db)):
    """Muestra todos los catálogos disponibles"""
    catalogos = crud.get_catalogos(db)
    return templates.TemplateResponse(
        "catalogos_list.html",
        {"request": request, "catalogos": catalogos}
    )

# === 2) Formulario de subida ===
@router.get("/new", response_class=HTMLResponse)
def new_catalogo_form(request: Request):
    """Renderiza la página para subir un nuevo catálogo"""
    return templates.TemplateResponse(
        "catalogo_upload.html",
        {"request": request}
    )

# === 3) Carga de catálogo ===
@router.post("/", status_code=303)
async def upload_catalogo(
    file: UploadFile = File(..., media_type="application/pdf"),
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """Valida y guarda un archivo PDF como nuevo catálogo"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos PDF")
    try:
        crud.create_catalogo(db, file)
        return RedirectResponse(url="/catalogos", status_code=303)
    except ValueError as e:
        # Nombre duplicado u otros errores de validación
        return templates.TemplateResponse(
            "catalogo_upload.html",
            {"request": request, "error": str(e)},
            status_code=400
        )

# === 4) Descarga de catálogo ===
@router.get("/download/{catalogo_id}")
def download_catalogo(
    catalogo_id: int,
    db: Session = Depends(deps.get_db)
):
    """Devuelve el PDF del catálogo solicitado"""
    catalogo = crud.get_catalogo(db, catalogo_id)
    if not catalogo:
        raise HTTPException(status_code=404, detail="Catálogo no encontrado")
    return FileResponse(
        path=catalogo.filepath,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{catalogo.filename}"'}
    )
