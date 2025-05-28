# app/core/currencies.py

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
