import sys
import os
from django.apps import AppConfig

class BcvServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bcv_service'

    def ready(self):
        # Evitar arranque duplicado en runserver (Django reloader)
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return

        # Importamos aquí para evitar problemas circulares
        from bcv_service import scheduler
        scheduler.start_scheduler()
