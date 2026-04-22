from django.db.models import F
from .models import PageVisit
from django.utils import timezone

class VisitCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Evitar contar visitas a la administración, archivos estáticos o la propia API interna de Django Ninja si se desea filtrar
        # Pero normalmente el usuario quiere ver cuántos entran al home o a la API pública.
        
        path = request.path
        
        # Ignorar peticiones de administración y estáticos
        if not path.startswith('/admin') and not path.startswith('/static') and not path.startswith('/favicon'):
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            
            # Clasificación simple de visitante
            visitor_type = 'WEB'
            bot_keywords = ['bot', 'crawler', 'spider', 'uptime', 'render', 'python-requests', 'postman']
            if any(keyword in user_agent for keyword in bot_keywords):
                visitor_type = 'BOT'
            elif path.startswith('/api/'):
                visitor_type = 'API'
            
            # Detección de Plataforma
            platform = 'PC'
            if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
                platform = 'MOBILE'
            elif 'tablet' in user_agent or 'ipad' in user_agent:
                platform = 'TABLET'
            
            # Captura de Referer (solo el dominio para limpieza)
            referer = request.META.get('HTTP_REFERER', '')
            if referer:
                from urllib.parse import urlparse
                referer = urlparse(referer).netloc
            else:
                referer = 'Directo / Favoritos'

            today = timezone.now().date()
            
            from django.db import IntegrityError
            try:
                # Usar get_or_create y F para evitar race conditions y ser eficiente
                visit, created = PageVisit.objects.get_or_create(
                    path=path,
                    date=today,
                    visitor_type=visitor_type,
                    platform=platform,
                    referer=referer[:500],
                    defaults={'count': 1}
                )
                
                if not created:
                    visit.count = F('count') + 1
                    visit.save()
            except IntegrityError:
                # Si falló por una race condition (otra petición creó el registro justo antes),
                # simplemente recuperamos el existente e incrementamos
                PageVisit.objects.filter(
                    path=path,
                    date=today,
                    visitor_type=visitor_type,
                    platform=platform,
                    referer=referer[:500]
                ).update(count=F('count') + 1)

        response = self.get_response(request)
        return response
