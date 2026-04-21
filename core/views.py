from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Avg, Q
from datetime import timedelta, date
import json
import pandas as pd
import io

from bcv_service.models import ExchangeRate, EconomicIndicator

def home_view(request):
    """Vista Nexo 21 con tasas, gráficas, historial e indicadores económicos."""
    today = timezone.now().date()
    
    # --- LÓGICA DE EXPORTACIÓN GENERAL ---
    export_format = request.GET.get('export', None)
    
    # Exportación de INDICADORES MACRO (Nueva función)
    if export_format and export_format.startswith('indicator_'):
        fmt = 'csv' if 'csv' in export_format else 'excel'
        indicator_name = request.GET.get('name')
        
        # Límite para todo el histórico (aprox 30 años = 360 registros)
        qs = EconomicIndicator.objects.filter(name=indicator_name).order_by('-fecha_referencia')[:1000]
        data = list(qs.values('name', 'value', 'unit', 'fecha_referencia'))
        df = pd.DataFrame(data)
        
        filename = f"historial_{indicator_name}_{today}.{'csv' if fmt == 'csv' else 'xlsx'}"
        
        if fmt == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            df.to_csv(path_or_buf=response, index=False, encoding='utf-8-sig')
            return response
        else:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    # --- DATOS PARA VISTA NORMAL ---
    bcv_usd = ExchangeRate.objects.filter(source="BCV", currency="USD", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    bcv_eur = ExchangeRate.objects.filter(source="BCV", currency="EUR", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    binance_usdt = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", is_active=True).order_by('-fecha_valor', '-fetched_at').first()
    
    interes_activa = EconomicIndicator.objects.filter(name='INTERES_ACTIVA').order_by('-fecha_referencia').first()
    interes_pasiva = EconomicIndicator.objects.filter(name='INTERES_PROM').order_by('-fecha_referencia').first()
    inflacion = EconomicIndicator.objects.filter(name='INFLACION').order_by('-fecha_referencia').first()

    selected_currency = request.GET.get('currency', 'USD').upper()
    period = request.GET.get('period', 'month')
    
    available_currencies = ExchangeRate.objects.order_by('currency').values_list('currency', flat=True).distinct()
    available_years = ExchangeRate.objects.dates('fecha_valor', 'year', order='DESC')
    available_years_list = [y.year for y in available_years]

    history_qs_table = ExchangeRate.objects.filter(currency=selected_currency).order_by('-fecha_valor', '-fetched_at')
    if period == 'month':
        history_qs_table = history_qs_table.filter(fecha_valor__month=today.month, fecha_valor__year=today.year)
    elif period == '3months':
        three_months_ago = today - timedelta(days=90)
        history_qs_table = history_qs_table.filter(fecha_valor__gte=three_months_ago)
    elif period.isdigit():
        history_qs_table = history_qs_table.filter(fecha_valor__year=int(period))

    # Exportación de TASAS (USD/EUR)
    if export_format in ['csv', 'excel']:
        data = list(history_qs_table.values('fecha_valor', 'currency', 'value', 'source'))
        df = pd.DataFrame(data)
        filename = f"historial_{selected_currency}_{period}.{'csv' if export_format == 'csv' else 'xlsx'}"
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            df.to_csv(path_or_buf=response, index=False, encoding='utf-8-sig')
            return response
        else:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    limit = 366 if period.isdigit() or period == 'all' else 50
    history_table = history_qs_table[:limit]
    
    # Gráfica
    history_qs_chart = ExchangeRate.objects.filter(source="BCV", currency="USD", is_active=True).order_by('-fecha_valor')[:15]
    chart_labels, chart_data_bcv, chart_data_binance = [], [], []
    for r in reversed(history_qs_chart):
        dia = r.fecha_valor
        chart_labels.append(dia.strftime("%d/%m"))
        chart_data_bcv.append(float(r.value))
        avg_binance = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", fecha_valor=dia).aggregate(Avg('value'))['value__avg']
        chart_data_binance.append(float(avg_binance) if avg_binance else None)
        
    context = {
        'bcv_usd': bcv_usd, 'bcv_eur': bcv_eur, 'binance_usdt': binance_usdt,
        'interes_activa': interes_activa, 'interes_pasiva': interes_pasiva, 'inflacion': inflacion,
        'selected_currency': selected_currency, 'period': period,
        'available_currencies': available_currencies, 'available_years': available_years_list,
        'history_table': history_table, 'last_update': timezone.now(),
        'chart_labels': json.dumps(chart_labels), 'chart_data_bcv': json.dumps(chart_data_bcv), 'chart_data_binance': json.dumps(chart_data_binance)
    }
    return render(request, 'index.html', context)
