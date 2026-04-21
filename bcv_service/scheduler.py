import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import datetime
from bcv_service.scraper import parse_bcv_rate, parse_binance_p2p
from bcv_service.models import ExchangeRate

logger = logging.getLogger(__name__)

def update_bcv_rates():
    """Función que ejecuta el scraper del BCV en segundo plano y guarda en BD"""
    logger.info("Iniciando tarea programada: Actualización BCV...")
    result = parse_bcv_rate()
    today = timezone.now().date()
    
    if result.get("success"):
        date_iso = result.get("date_iso")
        fecha_valor_dt = today
        if date_iso:
            try:
                fecha_valor_dt = datetime.strptime(date_iso, "%Y-%m-%d").date()
            except ValueError:
                pass

        for rate_data in result.get("rates", []):
            try:
                ExchangeRate.objects.get_or_create(
                    source="BCV",
                    currency=rate_data["currency"],
                    fecha_valor=fecha_valor_dt,
                    defaults={
                        "value": rate_data["value"],
                        "source_url": "https://www.bcv.org.ve/"
                    }
                )
            except Exception as e:
                logger.error(f"Error guardando tasa programada BCV {rate_data['currency']}: {e}")
        logger.info("Actualización BCV exitosa.")
    else:
        logger.error(f"Error en tarea BCV, intentando Fallback DolarAPI... Motivo: {result.get('error')}")
        from bcv_service.scraper import parse_fallback_api
        fallback_res = parse_fallback_api()
        
        if fallback_res.get("success"):
            date_iso = fallback_res.get("date_iso")
            fecha_valor_dt = today
            if date_iso:
                try:
                    fecha_valor_dt = datetime.strptime(date_iso, "%Y-%m-%d").date()
                except ValueError:
                    pass
            for rate_data in fallback_res.get("rates", []):
                try:
                    ExchangeRate.objects.get_or_create(
                        source="BCV", # Se guarda como BCV normal para no romper queries
                        currency=rate_data["currency"],
                        fecha_valor=fecha_valor_dt,
                        defaults={
                            "value": rate_data["value"],
                            "source_url": "https://ve.dolarapi.com/v1/dolares/oficial"
                        }
                    )
                except Exception as e:
                    pass
            logger.info("Actualización BCV vía Fallback exitosa.")
        else:
            logger.error("Error crítico: Ambos canales (BCV y Fallback) fallaron.")

def update_binance_rates():
    """Función que ejecuta el scraper de Binance en segundo plano y guarda en BD"""
    logger.info("Iniciando tarea programada: Actualización Binance P2P...")
    result = parse_binance_p2p()
    today = timezone.now().date()
    
    if result.get("success"):
        try:
            ExchangeRate.objects.create(
                source="BINANCE",
                currency="USDT",
                value=result["value"],
                fecha_valor=today,
                source_url="https://p2p.binance.com/"
            )
            logger.info("Actualización Binance exitosa.")
        except Exception as e:
            logger.error(f"Error guardando tasa programada Binance: {e}")
    else:
        logger.error(f"Error en tarea Binance: {result.get('error')}")


def update_indicators():
    """Tarea programada para revisar inflación y tasas de interés (Diaria)"""
    logger.info("Iniciando tarea programada: Verificación de Indicadores Económicos...")
    from bcv_service.scraper import update_economic_indicators
    update_economic_indicators()
    logger.info("Verificación de indicadores finalizada.")

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Caracas")
    
    # Binance cada 60 minutos (Balance ideal entre frescura y limpieza de BD)
    scheduler.add_job(update_binance_rates, 'interval', minutes=60, id='binance_job', replace_existing=True)
    
    # BCV cada 30 minutos
    scheduler.add_job(update_bcv_rates, 'interval', minutes=30, id='bcv_job', replace_existing=True)
    
    # Indicadores Macro una vez al día (a las 6:00 AM)
    scheduler.add_job(update_indicators, 'cron', hour=6, minute=0, id='indicators_job', replace_existing=True)

    scheduler.start()
    logger.info("Scheduler total (Tasas + Indicadores) iniciado.")
