import os
import django
from decimal import Decimal
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from bcv_service.models import EconomicIndicator

# Data proporcionada por el usuario (Parsed for Python)
raw_data = """
2026
Enero,47.34,58.68
2025
Diciembre,47.30,58.59
Noviembre,47.17,58.34
Octubre,47.33,58.66
Septiembre,47.47,58.95
Agosto,47.53,59.06
Julio,47.61,59.23
Junio,47.64,59.27
Mayo,47.61,59.22
Abril,47.65,59.29
Marzo,47.68,59.36
Febrero,47.69,59.39
Enero,47.69,59.38
2024
Diciembre,47.56,59.12
Noviembre,47.65,59.29
Octubre,47.65,59.30
Septiembre,47.62,59.23
Agosto,47.63,59.26
Julio,47.60,59.20
Junio,47.63,59.25
Mayo,47.60,59.20
Abril,47.49,58.98
Marzo,47.49,58.98
Febrero,47.30,58.59
Enero,46.92,57.84
2023
Diciembre,46.35,56.69
Noviembre,46.14,56.27
Octubre,46.07,56.14
Septiembre,45.64,55.27
Agosto,45.87,55.73
Julio,45.89,55.78
Junio,45.62,55.24
Mayo,44.81,53.62
Abril,46.79,57.57
Marzo,46.62,57.23
Febrero,46.49,56.97
Enero,47.65,59.30
2022
Diciembre,46.99,57.97
Noviembre,46.73,57.45
Octubre,46.84,57.68
Septiembre,46.50,56.99
Agosto,46.82,57.63
Julio,46.72,57.43
Junio,46.69,57.37
Mayo,47.07,58.13
Abril,45.98,55.95
Marzo,46.09,56.18
Febrero,47.00,57.99
Enero,47.18,58.35
2021
Diciembre,44.48,52.96
Noviembre,44.35,52.70
Octubre,46.43,56.86
Septiembre,44.48,52.96
Agosto,45.03,54.06
Julio,46.13,56.26
Junio,46.73,57.45
Mayo,46.66,57.32
Abril,47.36,58.71
Marzo,47.34,58.67
Febrero,40.67,45.34
Enero,31.80,39.59
2020
Diciembre,31.18,38.35
Noviembre,31.08,38.15
Octubre,31.46,38.92
Septiembre,31.38,38.76
Agosto,31.26,38.51
Julio,31.49,38.98
Junio,34.09,44.18
Mayo,36.66,49.32
Abril,39.00,54.00
Marzo,39.32,54.64
Febrero,36.05,48.10
Enero,31.06,38.13
2019
Diciembre,29.92,35.85
Noviembre,30.53,37.06
Octubre,25.97,27.95
Septiembre,27.33,30.67
Agosto,27.92,31.83
Julio,25.93,27.87
Junio,26.41,28.82
Mayo,27.31,30.62
Abril,26.15,28.31
Marzo,27.57,31.15
Febrero,28.14,32.28
Enero,18.45,22.40
2018
Diciembre,18.42,21.84
Noviembre,18.08,21.44
Octubre,17.92,20.84
Septiembre,18.38,21.90
Agosto,18.03,21.13
Julio,17.61,20.56
Junio,17.85,20.81
Mayo,17.80,20.99
Abril,18.26,21.93
Marzo,18.10,21.70
Febrero,18.55,22.58
Enero,17.85,21.19
2017
Diciembre,18.14,21.77
Noviembre,18.07,21.25
Octubre,18.05,21.53
Septiembre,18.09,21.53
Agosto,18.09,21.46
Julio,18.00,21.30
Junio,18.27,21.92
Mayo,18.11,21.56
Abril,18.08,21.46
Marzo,18.29,22.01
Febrero,18.33,21.78
Enero,17.76,20.76
2016
Diciembre,18.71,22.49
Noviembre,18.60,22.48
Octubre,18.69,22.37
Septiembre,18.25,21.73
Agosto,18.54,21.99
Julio,18.07,21.54
Junio,18.12,21.70
Mayo,18.36,21.36
Abril,17.88,21.07
Marzo,17.93,21.09
Febrero,17.05,19.54
Enero,17.86,20.61
2015
Diciembre,18.05,21.03
Noviembre,18.16,21.33
Octubre,18.13,21.35
Septiembre,17.86,20.89
Agosto,17.49,20.37
Julio,17.38,19.83
Junio,17.10,19.68
Mayo,16.99,19.46
Abril,17.22,19.51
Marzo,16.71,18.87
Febrero,16.65,18.76
Enero,16.76,18.70
2014
Diciembre,16.85,19.17
Noviembre,16.96,19.27
Octubre,16.65,18.39
Septiembre,16.16,17.76
Agosto,16.23,17.94
Julio,15.86,17.15
Junio,15.56,16.56
Mayo,15.54,16.57
Abril,15.44,16.38
Marzo,15.05,15.59
Febrero,15.54,16.27
Enero,15.12,15.73
2013
Diciembre,15.15,15.57
Noviembre,14.93,15.36
Octubre,14.99,15.47
Septiembre,15.13,15.76
Agosto,15.53,16.56
Julio,14.97,15.43
Junio,14.88,15.26
Mayo,15.07,15.63
Abril,15.09,15.67
Marzo,14.89,15.27
Febrero,15.47,16.43
Enero,14.66,14.82
2012
Diciembre,15.06,15.57
Noviembre,15.29,15.94
Octubre,15.50,16.49
Septiembre,15.65,16.80
Agosto,15.57,16.51
Julio,15.35,16.20
Junio,15.38,16.25
Mayo,15.63,16.75
Abril,15.41,16.31
Marzo,14.97,15.43
Febrero,15.18,15.65
Enero,15.70,16.90
2011
Diciembre,15.03,15.55
Noviembre,15.43,16.35
Octubre,16.39,18.28
Septiembre,16.00,17.50
Agosto,15.94,17.37
Julio,16.52,18.51
Junio,16.09,17.41
Mayo,16.64,18.17
Abril,16.37,17.69
Marzo,16.00,17.13
Febrero,16.37,17.85
Enero,16.29,17.53
2010
Diciembre,16.45,17.89
Noviembre,16.25,17.76
Octubre,16.38,17.70
Septiembre,16.10,17.43
Agosto,16.28,17.97
Julio,16.34,17.73
Junio,16.10,17.65
Mayo,16.40,17.93
Abril,16.23,17.95
Marzo,16.44,18.36
Febrero,16.65,18.55
Enero,16.74,18.96
2009
Diciembre,16.97,18.94
Noviembre,17.05,18.84
Octubre,17.62,20.35
Septiembre,16.58,18.62
Agosto,17.04,19.56
Julio,17.26,20.01
Junio,17.56,20.41
Mayo,18.77,21.54
Abril,18.77,21.46
Marzo,19.74,22.37
Febrero,19.98,22.89
Enero,19.76,22.38
2008
Diciembre,19.65,21.67
Noviembre,20.24,23.18
Octubre,19.82,22.62
Septiembre,19.68,22.31
Agosto,20.09,22.83
Julio,20.30,23.47
Junio,20.09,22.38
Mayo,20.85,24.00
Abril,18.35,22.62
Marzo,18.17,22.24
Febrero,17.56,22.68
Enero,18.53,24.14
2007
Diciembre,16.44,21.73
Noviembre,15.75,19.91
Octubre,14.00,16.96
Septiembre,13.79,16.53
Agosto,13.86,16.59
Julio,13.51,16.17
Junio,12.53,14.91
Mayo,13.03,15.94
Abril,13.05,15.99
Marzo,12.53,14.94
Febrero,12.82,15.50
Enero,12.92,15.78
2006
Diciembre,12.64,15.23
Noviembre,12.63,15.20
Octubre,12.46,14.87
Septiembre,12.32,14.42
Agosto,12.43,14.79
Julio,12.29,14.50
Junio,11.94,13.83
Mayo,12.15,14.17
Abril,12.11,14.16
Marzo,12.31,14.55
Febrero,12.76,15.04
Enero,12.71,14.93
2005
Diciembre,12.79,14.40
Noviembre,12.95,15.07
Octubre,13.18,15.26
Septiembre,12.71,14.68
Agosto,13.33,15.85
Julio,13.53,15.82
Junio,13.47,15.25
Mayo,14.02,16.37
Abril,13.96,15.45
Marzo,14.44,16.48
Febrero,14.21,16.04
Enero,14.93,16.30
2004
Diciembre,15.25,16.00
Noviembre,14.51,16.11
Octubre,15.02,17.01
Septiembre,15.20,16.92
Agosto,15.01,17.58
Julio,14.45,17.22
Junio,14.92,17.08
Mayo,15.40,17.68
Abril,15.22,17.97
Marzo,15.20,17.56
Febrero,14.46,18.08
Enero,15.09,18.38
2003
Diciembre,16.83,19.48
Noviembre,17.67,19.82
Octubre,16.87,21.13
Septiembre,19.99,22.37
Agosto,18.74,23.29
Julio,18.49,22.09
Junio,18.33,23.17
Mayo,20.12,25.50
Abril,24.52,29.01
Marzo,25.05,31.80
Febrero,29.12,33.55
Enero,31.63,36.96
2002
Diciembre,29.99,33.86
Noviembre,30.47,33.08
Octubre,29.44,32.72
Septiembre,26.92,30.68
Agosto,26.92,30.89
Julio,29.90,32.80
Junio,31.64,35.15
Mayo,36.20,38.49
Abril,43.59,48.46
Marzo,50.10,55.84
Febrero,39.10,53.56
Enero,28.91,35.35
2001
Diciembre,23.57,27.66
Noviembre,21.51,26.75
Octubre,25.59,31.31
Septiembre,27.62,35.86
Agosto,19.69,24.87
Julio,18.54,22.76
Junio,18.50,23.37
Mayo,16.56,20.82
Abril,16.05,20.02
Marzo,16.17,21.07
Febrero,16.17,21.14
Enero,17.34,22.43
2000
Diciembre,17.76,21.98
Noviembre,17.70,21.67
Octubre,17.43,21.09
Septiembre,18.84,23.69
Agosto,19.28,23.69
Julio,18.81,23.42
Junio,21.31,26.19
Mayo,19.04,23.06
Abril,20.49,25.98
Marzo,19.78,25.14
Febrero,22.10,28.97
Enero,23.76,29.15
1999
Diciembre,22.69,28.13
Noviembre,22.95,28.14
Octubre,21.74,29.00
Septiembre,21.12,28.70
Agosto,21.03,29.33
Julio,23.00,30.19
Junio,24.84,31.03
Mayo,24.80,28.20
Abril,27.26,30.28
Marzo,30.55,34.38
Febrero,35.07,39.73
Enero,36.73,38.96
1998
Diciembre,39.72,44.10
Noviembre,42.71,44.95
Octubre,47.07,49.61
Septiembre,63.84,72.23
Agosto,51.28,56.78
Julio,53.25,60.92
Junio,38.79,42.22
Mayo,38.18,41.42
Abril,32.27,36.03
Marzo,30.84,35.79
Febrero,29.46,34.86
Enero,21.51,24.15
1997
Diciembre,21.14,25.24
Noviembre,18.72,21.76
Octubre,18.34,21.80
Septiembre,18.73,22.11
Agosto,19.86,24.16
Junio,20.53,26.14
"""

meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

def seed_history():
    current_year = 0
    records_activa = 0
    records_prom = 0
    
    lines = raw_data.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if line.isdigit() and len(line) == 4:
            current_year = int(line)
            continue
        
        parts = line.split(',')
        if len(parts) == 3:
            mes_nombre = parts[0]
            val_prom = Decimal(parts[1].replace(',', '.'))
            val_act = Decimal(parts[2].replace(',', '.'))
            
            mes_num = meses.get(mes_nombre)
            if mes_num and current_year:
                fecha = date(current_year, mes_num, 1)
                
                # Guardar Tasa Activa
                EconomicIndicator.objects.get_or_create(
                    name='INTERES_ACTIVA',
                    fecha_referencia=fecha,
                    defaults={'value': val_act, 'unit': '%'}
                )
                records_activa += 1
                
                # Guardar Tasa Promedio
                EconomicIndicator.objects.get_or_create(
                    name='INTERES_PROM',
                    fecha_referencia=fecha,
                    defaults={'value': val_prom, 'unit': '%'}
                )
                records_prom += 1

    print(f"✅ Inyección completada: {records_activa} registros Activa, {records_prom} registros Promedio.")

if __name__ == "__main__":
    seed_history()
