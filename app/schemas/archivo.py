from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ArchivoBase(BaseModel):
    filename: str


class ArchivoCreate(ArchivoBase):
    pass


class ArchivoOut(ArchivoBase):
    id: int
    filepath: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
