from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from ..core.templates import templates
from .. import crud, schemas, deps

router = APIRouter(
    prefix="/catalogos",
    tags=["catalogos"]
)

@router.get("/", response_class=HTMLResponse)
def list_catalogos(request: Request, db: Session = Depends(deps.get_db)):
    catalogos = crud.get_catalogos(db)
    return templates.TemplateResponse(
        "catalogos_list.html",
        {"request": request, "catalogos": catalogos}
    )

@router.get("/new", response_class=HTMLResponse)
def new_catalogo_form(request: Request):
    return templates.TemplateResponse(
        "catalogo_upload.html",
        {"request": request}
    )

@router.post("/", status_code=303)
async def upload_catalogo(
    file: UploadFile = File(..., media_type="application/pdf"),
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Solo se admiten archivos PDF")
    try:
        crud.create_catalogo(db, file)
        return RedirectResponse(url="/catalogos", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse(
            "catalogo_upload.html",
            {"request": request, "error": str(e)},
            status_code=400
        )

@router.get("/download/{catalogo_id}")
def download_catalogo(
    catalogo_id: int,
    db: Session = Depends(deps.get_db)
):
    catalogo = crud.get_catalogo(db, catalogo_id)
    if not catalogo:
        raise HTTPException(404, "Catálogo no encontrado")
    return FileResponse(
        path=catalogo.filepath,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{catalogo.filename}"'
        }
    )
