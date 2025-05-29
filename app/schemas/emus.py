from enum import Enum


class TipoMovimientoDinero(str, Enum):
    INGRESO = "INGRESO"
    EGRESO = "EGRESO"
