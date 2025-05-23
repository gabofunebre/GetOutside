# app/routers/catalogos.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from .. import database, models, schemas, crud
from ..core.templates import templates

router = APIRouter(prefix="/catalogos", tags=["Catálogos"])

# =============================================
# Dependencia para obtener sesión de base de datos
# =============================================
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================
# 1. Vista HTML simple de catálogos (lectura)
# =============================================
@router.get("/", response_class=HTMLResponse)
def catalogos_html(request: Request, db: Session = Depends(get_db)):
    catalogos = crud.get_catalogos(db)
    return templates.TemplateResponse("catalogos.html", {"request": request, "catalogos": catalogos})

# =============================================
# 2. Vista HTML para edición de catálogos
# =============================================
@router.get("/edit", response_class=HTMLResponse)
def catalogos_edit_view(request: Request, db: Session = Depends(get_db)):
    catalogos = crud.get_catalogos(db)
    return templates.TemplateResponse("catalogos_edit.html", {"request": request, "catalogos": catalogos})

# =============================================
# 3. Subida de nuevo catálogo (formulario y API)
# =============================================
@router.get("/new", response_class=HTMLResponse)
def new_catalogo_form(request: Request):
    return templates.TemplateResponse("catalogo_upload.html", {"request": request})

@router.post("/", status_code=303)
async def upload_catalogo(file: UploadFile = File(..., media_type="application/pdf"), db: Session = Depends(get_db), request: Request = None):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos PDF")
    try:
        crud.create_catalogo(db, file)
        return RedirectResponse(url="/catalogos", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse("catalogo_upload.html", {"request": request, "error": str(e)}, status_code=400)

# =============================================
# 4. Descarga de catálogo por ID
# =============================================
@router.get("/download/{catalogo_id}")
def download_catalogo(catalogo_id: int, db: Session = Depends(get_db)):
    catalogo = crud.get_catalogo(db, catalogo_id)
    if not catalogo:
        raise HTTPException(status_code=404, detail="Catálogo no encontrado")
    return FileResponse(
        path=catalogo.filepath,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{catalogo.filename}"'}
    )

# =============================================
# 5. API JSON de catálogos (frontend consumo)
# =============================================
@router.get("/api", response_model=list[schemas.CatalogoOut])
def catalogos_json(db: Session = Depends(get_db)):
    return crud.get_catalogos(db)

# =============================================
# 6. Actualización de nombre de catálogo
# =============================================
@router.put("/id/{catalogo_id}", response_model=schemas.CatalogoOut)
def actualizar_catalogo(catalogo_id: int, payload: schemas.CatalogoUpdate, db: Session = Depends(get_db)):
    try:
        catalogo = crud.update_catalogo(db, catalogo_id, payload.filename)
        return catalogo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================
# 7. Eliminación de catálogo (solo si no está en uso)
# =============================================
@router.delete("/id/{catalogo_id}")
def eliminar_catalogo(catalogo_id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_catalogo(db, catalogo_id)
        return {"detail": "Catálogo eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
