# app/core/templates.py
from fastapi.templating import Jinja2Templates

# instancia única de Jinja2 para todo el proyecto
templates = Jinja2Templates(directory="app/templates")
