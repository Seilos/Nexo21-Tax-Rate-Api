from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from typing import Optional, List
from decimal import Decimal
from django.utils import timezone
from .scraper import parse_bcv_rate, parse_binance_p2p
from .models import ExchangeRate
from datetime import datetime, date
from django.core.cache import cache
from functools import wraps

api = NinjaAPI(title="BCV & Exchange Rates API", description="Microservicio de Tasas de Cambio")

# --- RATE LIMITING DECORATOR ---
def rate_limit(max_requests=60, timeout=60):
    """Limita la cantidad de peticiones por IP en un tiempo dado (segundos)"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
            key = f"rate_limit_{func.__name__}_{ip}"
            
            count = cache.get(key, 0)
            if count >= max_requests:
                raise HttpError(429, "Too Many Requests - Has excedido tu límite gratuito de consultas temporales.")
            
            cache.set(key, count + 1, timeout)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


class RateResponse(Schema):
    source: str
    currency: str = "USD"
    value: Decimal
    date_text: Optional[str] = None
    fetched_at: str
    success: bool
    error: Optional[str] = None

class RateHistoryResponse(Schema):
    success: bool
    rates: List[RateResponse] = []
    error: Optional[str] = None


@api.get("/rates/bcv/latest", response=RateResponse, summary="Obtener tasa actual")
@rate_limit(max_requests=30, timeout=60)
def get_latest_bcv_rate(request, currency: str = "USD"):
    today = timezone.now().date()
    currency = currency.upper()
    
    # Simplemente buscar en caché
    cached_rate = ExchangeRate.objects.filter(source="BCV", currency=currency, is_active=True, fecha_valor__gte=today).order_by('fecha_valor', '-fetched_at').first()
    if not cached_rate:
         cached_rate = ExchangeRate.objects.filter(source="BCV", currency=currency, is_active=True, fecha_valor=today).first()
         
    if not cached_rate:
         # Fallback Histórico
         cached_rate = ExchangeRate.objects.filter(source="BCV", currency=currency, is_active=True).order_by('-fecha_valor', '-fetched_at').first()

    if cached_rate:
         return {
            "source": "BCV",
            "currency": cached_rate.currency,
            "value": cached_rate.value,
            "date_text": f"Valor del {cached_rate.fecha_valor}",
            "fetched_at": cached_rate.fetched_at.isoformat(),
            "success": True
         }
         
    return {"success": False, "source": "BCV", "error": "No hay tasas disponibles en la BD.", "value": 0, "fetched_at": timezone.now().isoformat()}


@api.get("/rates/bcv/history", response=RateHistoryResponse, summary="Obtener historial de tasas")
@rate_limit(max_requests=10, timeout=60)
def get_bcv_history(request, from_date: Optional[date] = None, to_date: Optional[date] = None, currency: str = "USD"):
    currency = currency.upper()
    qs = ExchangeRate.objects.filter(source="BCV", currency=currency, is_active=True)
    
    if from_date:
        qs = qs.filter(fecha_valor__gte=from_date)
    if to_date:
         qs = qs.filter(fecha_valor__lte=to_date)
    
    qs = qs.order_by('-fecha_valor')[:30]
    
    results = []
    for r in qs:
        results.append({
             "source": r.source,
             "currency": r.currency,
             "value": r.value,
             "date_text": f"Histórico del {r.fecha_valor}",
             "fetched_at": r.fetched_at.isoformat(),
             "success": True
        })
    return {"success": True, "rates": results}


@api.get("/rates/binance/latest", response=RateResponse, summary="Obtener tasa USDT Binance P2P")
@rate_limit(max_requests=30, timeout=60)
def get_latest_binance_rate(request):
    cached_rate = ExchangeRate.objects.filter(source="BINANCE", currency="USDT", is_active=True).order_by('-fecha_valor', '-fetched_at').first()

    if cached_rate:
        return {
            "source": "BINANCE",
            "currency": "USDT",
            "value": cached_rate.value,
            "date_text": f"Valor de Binance P2P",
            "fetched_at": cached_rate.fetched_at.isoformat(),
            "success": True
        }

    return {"success": False, "source": "BINANCE", "error": "No hay datos de Binance. Scheduler ejecutando.", "value": 0, "fetched_at": timezone.now().isoformat()}

class IndicatorResponse(Schema):
    name: str
    value: Decimal
    unit: str
    fecha_referencia: date
    fetched_at: str
    success: bool = True

@api.get("/indicators/latest", response=List[IndicatorResponse], summary="Obtener últimos indicadores macro")
@rate_limit(max_requests=20, timeout=60)
def get_indicators(request):
    from .models import EconomicIndicator
    indicadores = []
    for code, label in EconomicIndicator.INDICATOR_CHOICES:
        ind = EconomicIndicator.objects.filter(name=code).order_by('-fecha_referencia').first()
        if ind:
            indicadores.append({
                "name": ind.get_name_display(),
                "value": ind.value,
                "unit": ind.unit,
                "fecha_referencia": ind.fecha_referencia,
                "fetched_at": ind.fetched_at.isoformat()
            })
    return indicadores
