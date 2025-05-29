from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from app.crud import inventario
from app.schemas.catalogo import CatalogoOut, CatalogoUpdate
from app.core.templates import templates
from app.core.deps import get_db

router = APIRouter(prefix="/catalogos", tags=["Catálogos"])


# ======================================================
# 1. Vista HTML de lectura de catálogos (solo visualizar)
# ======================================================
@router.get("/", response_class=HTMLResponse)
def catalogos_html(request: Request, db: Session = Depends(get_db)):
    catalogos = inventario.get_catalogos(db)
    return templates.TemplateResponse(
        "catalogos.html", {"request": request, "catalogos": catalogos}
    )


# ============================================================
# 2. Vista HTML para editar nombre de catálogos existentes
# ============================================================
@router.get("/edit", response_class=HTMLResponse)
def catalogos_edit_view(request: Request, db: Session = Depends(get_db)):
    catalogos = inventario.get_catalogos(db)
    return templates.TemplateResponse(
        "catalogos_edit.html", {"request": request, "catalogos": catalogos}
    )


# ================================================
# 3. Formulario HTML para subir un nuevo catálogo
# ================================================
@router.get("/new", response_class=HTMLResponse)
def new_catalogo_form(request: Request):
    return templates.TemplateResponse("catalogo_upload.html", {"request": request})


# ======================================================
# 4. Subida de un nuevo catálogo (archivo PDF obligatorio)
# ======================================================
@router.post("/", status_code=303)
async def upload_catalogo(
    file: UploadFile = File(..., media_type="application/pdf"),
    db: Session = Depends(get_db),
    request: Request = None,
):
    # Validación de tipo de archivo
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos PDF")

    # Procesamiento e inserción en base de datos
    try:
        inventario.create_catalogo(db, file)
        return RedirectResponse(url="/catalogos", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse(
            "catalogo_upload.html",
            {"request": request, "error": str(e)},
            status_code=400,
        )


# =======================================================
# 5. Descarga directa de un catálogo por su ID (PDF)
# =======================================================
@router.get("/download/{catalogo_id}")
def download_catalogo(catalogo_id: int, db: Session = Depends(get_db)):
    catalogo = inventario.get_catalogo(db, catalogo_id)
    if not catalogo:
        raise HTTPException(status_code=404, detail="Catálogo no encontrado")

    return FileResponse(
        path=catalogo.filepath,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{catalogo.filename}"'},
    )


# ====================================================================
# 6. API JSON: listado de catálogos para frontend u otros consumidores
# ====================================================================
@router.get("/api", response_model=List[CatalogoOut])
def catalogos_json(db: Session = Depends(get_db)):
    raw = inventario.get_catalogos(db)
    return [CatalogoOut.from_orm(c) for c in raw]


# ===============================================================
# 7. Actualización del nombre de un catálogo a través de su ID
# ===============================================================
@router.put("/id/{catalogo_id}", response_model=CatalogoOut)
def actualizar_catalogo(
    catalogo_id: int, payload: CatalogoUpdate, db: Session = Depends(get_db)
):
    try:
        updated = inventario.update_catalogo(db, catalogo_id, payload.filename)
        return CatalogoOut.from_orm(updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================================
# 8. Eliminación de un catálogo (solo si no está en uso)
# ==========================================================
@router.delete("/id/{catalogo_id}")
def eliminar_catalogo(catalogo_id: int, db: Session = Depends(get_db)):
    try:
        inventario.delete_catalogo(db, catalogo_id)
        return {"detail": "Catálogo eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
