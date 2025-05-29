#app/models/enums.py

import enum


class TipoMov(enum.Enum):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"


class TipoMovimientoDinero(enum.Enum):
    INGRESO = "INGRESO"
    EGRESO = "EGRESO"
