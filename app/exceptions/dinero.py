# app/exceptions/dinero.py

class DineroError(Exception):
    """Error base para operaciones relacionadas con dinero."""
    pass


class MovimientoInvalido(DineroError):
    """El movimiento tiene datos inválidos o violaciones de integridad."""
    pass


class MovimientoNoRegistrado(DineroError):
    """No se pudo guardar el movimiento en la base de datos."""
    pass


class ConversionMonedaFallida(DineroError):
    """Fallo al intentar convertir monedas (API externa o datos faltantes)."""
    pass


class ConsultaTenenciasFallida(Exception):
    pass

class ActualizacionTenenciasFallida(Exception):
    pass