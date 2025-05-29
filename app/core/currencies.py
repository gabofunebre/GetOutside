# app/core/currencies.py

import requests

# === Lista de monedas admitidas con etiquetas ===
# Se usa en formularios y reportes para asegurar consistencia visual.
TOP_CURRENCIES = [
    {"code": "NZD", "label": "🇳🇿"},
    {"code": "AUD", "label": "🇦🇺"},
    {"code": "USD", "label": "🇺🇸"},
    {"code": "EUR", "label": "🇪🇺"},
]

# === Diccionario auxiliar para lookup rápido por código ===
# Se usa para reemplazar 'USD' por '🇺🇸 USD' por ejemplo.
CURRENCY_LABELS = {c["code"]: c["label"] for c in TOP_CURRENCIES}



#  Api de conversión en uso
FRANKFURTER_API_URL = "https://api.frankfurter.app/latest"

# === Función para obtener tasas de cambio desde Frankfurter API ===
def get_exchange_rates(
    base: str, symbols: set[str], api_url: str
) -> tuple[dict[str, float], str | None]:
    """
    Consulta la API de Frankfurter para obtener tasas de cambio desde `symbols` hacia `base`.

    :param base: Código de moneda objetivo (por ejemplo, "NZD")
    :param symbols: Conjunto de códigos de moneda originales (por ejemplo, {"USD", "EUR"})
    :param api_url: URL base de la API de Frankfurter (ej. "https://api.frankfurter.app/latest")
    :return: Una tupla con (dict de tasas, mensaje de error o None)
    """
    try:
        if not symbols:
            return {}, None

        params = {"base": base, "symbols": ",".join(symbols)}
        resp = requests.get(api_url, params=params, timeout=5)
        resp.raise_for_status()
        rates = resp.json().get("rates", {})
        return rates, None

    except Exception:
        return (
            {},
            "No fue posible obtener los tipos de cambio. Se muestran solo los valores en moneda original.",
        )
