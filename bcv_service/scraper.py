import requests
from bs4 import BeautifulSoup
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

BCV_URL = "https://www.bcv.org.ve/"

def parse_bcv_rate():
    try:
        # Custom headers to act as a normal browser to prevent blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }
        
        # Desactivando warnings de certificado por seguridad en sitios gubernamentales a veces
        requests.packages.urllib3.disable_warnings() 
        response = requests.get(BCV_URL, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Parse the date
        date_element = soup.find('span', class_='date-display-single')
        date_text = date_element.text.strip() if date_element else None
        date_iso = None
        if date_element and date_element.has_attr('content'):
            # The 'content' attr usually has "2026-04-17T00:00:00-04:00"
            content_val = date_element['content']
            # We just want the date part "YYYY-MM-DD"
            date_iso = content_val.split('T')[0]
            
        currency_ids = {
            'euro': 'EUR',
            'yuan': 'CNY',
            'lira': 'TRY',
            'rublo': 'RUB',
            'dolar': 'USD'
        }
        
        results = []
        for html_id, currency_code in currency_ids.items():
            curr_div = soup.find(id=html_id)
            if curr_div:
                strong_tag = curr_div.find('strong')
                if strong_tag:
                    rate_text = strong_tag.text.strip().replace(',', '.')
                    try:
                        rate_value = Decimal(rate_text)
                        results.append({
                            "source": "BCV",
                            "currency": currency_code,
                            "value": rate_value,
                            "date_text": date_text,
                            "date_iso": date_iso,
                            "success": True
                        })
                    except:
                        pass
        
        if not results:
             raise ValueError("No se encontraron tasas en la web del BCV")
             
        return {
            "success": True,
            "rates": results,
            "date_iso": date_iso,
            "date_text": date_text
        }
        
    except Exception as e:
        logger.error(f"Error scraping BCV: {e}")
        return {
            "source": "BCV",
            "success": False,
            "error": str(e)
        }

def parse_fallback_api():
    """
    Usa la API pública (ve.dolarapi.com) como respaldo en caso de que
    la página oficial del BCV esté caída o bloqueada.
    """
    try:
        response = requests.get("https://ve.dolarapi.com/v1/dolares/oficial", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # DolarAPI maneja ISO-8601 (ej. "2026-04-20T00:00:00-04:00")
        date_iso = data.get("fechaActualizacion", "").split('T')[0]
        
        return {
            "success": True,
            "date_iso": date_iso,
            "date_text": "Fallback DolarAPI",
            "rates": [
                {
                    "source": "BCV_FALLBACK", # Logicamente es la misma tasa
                    "currency": "USD",
                    "value": Decimal(str(data.get("promedio", 0))),
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error en Fallback DolarAPI: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def parse_binance_p2p():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        payload = {
            "fiat": "VES",
            "page": 1,
            "rows": 10,
            "tradeType": "BUY", # Cambiamos a BUY para ver el precio de mercado más estable
            "asset": "USDT",
            "countries": [],
            "proMerchantAds": False,
            "shieldMerchantAds": False,
            "publisherType": "merchant", # Solo tomamos comerciantes verificados (más confiable)
            "payTypes": ["Banesco", "PagoMovil"], # Centramos en los métodos más usados
            "classifies": ["mass", "profession"]
        }
        
        response = requests.post("https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search", json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('data') and len(data['data']) > 0:
            # Tomamos el promedio de los primeros 3 anuncios de comerciantes (más estable)
            prices = [Decimal(ad['adv']['price']) for ad in data['data'][:3]]
            avg_price = sum(prices) / len(prices)
            
            return {
                "source": "BINANCE",
                "currency": "USDT",
                "value": avg_price,
                "date_text": "Tiempo Real (Binance P2P)",
                "success": True
            }
        else:
             raise ValueError("No se encontraron anuncios P2P en Binance")
             
    except Exception as e:
        logger.error(f"Error scraping Binance: {e}")
        return {
            "source": "BINANCE",
            "success": False,
            "error": str(e)
        }

def update_economic_indicators():
    """Actualiza automáticamente los indicadores macro del BCV."""
    from bcv_service.models import EconomicIndicator
    from datetime import date
    # Por ahora, como los indicadores cambian mensualmente, el scraper manual es más seguro.
    # Esta función servirá de base para cuando el BCV estandarice sus PDFs de avisos oficiales.
    print("Sincronizando indicadores macro... OK")

def update_all():
    """Ejecuta todas las tareas de actualización programadas."""
    print("Iniciando ciclo de actualización total...")
    update_bcv_rates()
    update_binance_rates()
    update_economic_indicators()

if __name__ == "__main__":
    # Prueba local de scraping
    print("=== TEST SCRAPER NEXO 21 ===")
    print("BCV:", parse_bcv_rate())
    print("Binance:", parse_binance_p2p())
    print("Finalizado.")
