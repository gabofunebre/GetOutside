import os

# Ruta estática persistente donde se guardan los archivos subidos desde la app.
# Se define como ruta relativa para que coincida con el directorio que se
# expone como archivos estáticos (montado desde ``main.py``). Usar una ruta
# absoluta rompía la correspondencia y provocaba que las fotos no se
# sirvieran correctamente.
BASE_UPLOADS_DIR = os.path.join("app", "static", "uploads")

# Rutas parciales por servicio.
CATALOGOS_DIR = os.path.join(BASE_UPLOADS_DIR, "catalogos")
ARCHIVOS_DIR = os.path.join(BASE_UPLOADS_DIR, "archivos")
PRODUCT_PHOTOS_DIR = os.path.join(BASE_UPLOADS_DIR, "products_photos")


# Usada para traer los movimientos de dinero de la base.
DEFAULT_MOVIMIENTOS_LIMIT = 30
