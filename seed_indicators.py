import os
import django
import sys
from datetime import date
from decimal import Decimal

# Configurar entorno Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from bcv_service.models import EconomicIndicator

def seed_indicators():
    print("Inyectando Indicadores Económicos (Marzo/Abril 2026)...")
    
    data = [
        ('INTERES_PRES', 58.60, '%', date(2026, 3, 31)), # Tasa Activa
        ('INTERES_PRES', 47.34, '%', date(2026, 3, 1)),  # Tasa Promedio
        ('INFLACION', 13.10, '%', date(2026, 3, 1)),
        ('RESERVAS', 9850.00, 'M USD', date(2026, 4, 15)), # Valor estimado referencial
    ]
    
    total = 0
    for name, val, unit, f_ref in data:
        obj, created = EconomicIndicator.objects.get_or_create(
            name=name, value=Decimal(str(val)), fecha_referencia=f_ref,
            defaults={'unit': unit}
        )
        if created: total += 1
        
    print(f"Éxito: Se inyectaron {total} indicadores.")

if __name__ == "__main__":
    seed_indicators()
