import os
import django
import sys
from datetime import date
from decimal import Decimal

# Configurar entorno Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from bcv_service.models import ExchangeRate

# Datos combinados: Usuario (2025-2026) + Scraped (2023-2024)
data_points = [
    # --- 2024 ---
    ("2024-12-30", 51.93, 54.11), ("2024-12-18", 50.54, 53.04), ("2024-11-29", 46.85, 49.38),
    ("2024-11-12", 44.75, 47.62), ("2024-10-31", 42.71, 46.37), ("2024-10-15", 38.89, 42.44),
    ("2024-09-30", 36.85, 41.14), ("2024-09-13", 36.74, 40.54), ("2024-08-30", 36.63, 40.59),
    ("2024-08-15", 36.65, 40.38), ("2024-07-31", 36.61, 39.59), ("2024-07-15", 36.49, 39.77),
    ("2024-06-28", 36.40, 39.26), ("2024-06-14", 36.43, 39.22), ("2024-05-31", 36.51, 39.46),
    ("2024-05-15", 36.57, 39.59), ("2024-04-30", 36.43, 39.06), ("2024-04-15", 36.29, 38.64),
    ("2024-03-27", 36.33, 39.38), ("2024-03-13", 36.24, 39.54), ("2024-02-29", 36.15, 39.11),
    ("2024-02-15", 36.27, 38.93), ("2024-01-31", 36.26, 39.31), ("2024-01-15", 36.03, 39.48),
    ("2024-01-02", 35.96, 39.82),
    # --- 2023 ---
    ("2023-12-29", 35.93, 39.90), ("2023-12-18", 35.72, 39.01), ("2023-11-30", 35.49, 38.92),
    ("2023-11-15", 35.34, 38.45), ("2023-10-31", 35.06, 37.19), ("2023-10-16", 34.87, 36.75),
    ("2023-09-29", 34.42, 36.45), ("2023-09-14", 33.44, 35.92), ("2023-08-31", 32.51, 35.35),
    ("2023-08-15", 31.50, 34.45), ("2023-07-31", 29.50, 32.55), ("2023-07-14", 28.46, 32.01),
    ("2023-06-30", 28.01, 30.55), ("2023-06-15", 27.17, 29.45), ("2023-05-31", 26.25, 28.01),
    ("2023-05-15", 25.44, 27.63), ("2023-04-28", 24.75, 27.31), ("2023-04-14", 24.48, 27.05),
    ("2023-03-31", 24.52, 26.68), ("2023-03-15", 24.06, 25.46), ("2023-02-28", 24.36, 25.85),
    ("2023-02-15", 24.34, 26.06), ("2023-01-31", 22.37, 24.34), ("2023-01-16", 19.45, 21.07),
    ("2023-01-03", 17.56, 18.74),
]

def seed_full_history():
    print("Inyectando historial profundo (2023-2024)...")
    total = 0
    for f_str, usd, eur in data_points:
        f_date = date.fromisoformat(f_str)
        # USD
        _, c_usd = ExchangeRate.objects.get_or_create(
            source="BCV", currency="USD", fecha_valor=f_date,
            defaults={'value': Decimal(str(usd)), 'source_url': 'https://dolarvzla.com/'}
        )
        # EUR
        _, c_eur = ExchangeRate.objects.get_or_create(
            source="BCV", currency="EUR", fecha_valor=f_date,
            defaults={'value': Decimal(str(eur)), 'source_url': 'https://dolarvzla.com/'}
        )
        if c_usd: total += 1
        if c_eur: total += 1
    
    print(f"Éxito: Se inyectaron {total} nuevos registros históricos.")

if __name__ == "__main__":
    seed_full_history()
