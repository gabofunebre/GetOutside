import os

# Ruta estática persistente donde se guardan los archivos subidos desde la ap
BASE_UPLOADS_DIR = "/app/static/uploads"

# Rutas parciales por servicio.
CATALOGOS_DIR = os.path.join(BASE_UPLOADS_DIR, "catalogos")
ARCHIVOS_DIR = os.path.join(BASE_UPLOADS_DIR, "archivos")


# Usada para traer los movimientos de dinero de la base.
DEFAULT_MOVIMIENTOS_LIMIT = 30
