from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CatalogoBase(BaseModel):
    """
    Campos base para gestión de catálogos PDF.
    """

    filename: str  # Nombre del archivo


class CatalogoCreate(CatalogoBase):
    """
    Entrada para subir un nuevo catálogo.
    """

    pass


class Catalogo(BaseModel):
    """
    Salida de catálogo con metadatos.
    """

    id: int  # ID autogenerado
    filepath: str  # Ruta en servidor
    uploaded_at: datetime  # Fecha de subida

    model_config = ConfigDict(from_attributes=True)


class CatalogoOut(BaseModel):
    """
    Salida simplificada de catálogo para relaciones.
    """

    id: int
    filename: str

    model_config = ConfigDict(from_attributes=True)


class CatalogoUpdate(BaseModel):
    """
    Entrada para editar el nombre de un catálogo existente.
    """

    filename: str
