from django.db import models

class ExchangeRate(models.Model):
    SOURCE_CHOICES = (
        ('BCV', 'Banco Central de Venezuela'),
        ('PARALELO', 'Dólar Paralelo'),
        ('BINANCE', 'Binance P2P'),
    )
    
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='BCV', verbose_name="Fuente de la Tasa")
    value = models.DecimalField(max_digits=20, decimal_places=8, verbose_name="Valor de la Tasa")
    fecha_valor = models.DateField(verbose_name="Fecha Valor Oficial", help_text="La fecha dada por la fuente para esta tasa")
    
    currency = models.CharField(max_length=10, default='USD', verbose_name="Moneda", help_text="Ej: USD, EUR, CNY, TRY, RUB")
    
    fetched_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Extracción (Scraping)")
    source_url = models.URLField(blank=True, null=True, verbose_name="URL de Origen")
    is_active = models.BooleanField(default=True, verbose_name="¿Es la tasa activa/actual?")
    
    class Meta:
        verbose_name = "Tasa de Cambio"
        verbose_name_plural = "Tasas de Cambio"
        ordering = ['-fecha_valor', '-fetched_at']
        
    def __str__(self):
        return f"{self.get_source_display()} - {self.value} {self.currency} to VED ({self.fecha_valor})"

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        # El valor debe ser positivo
        if self.value <= 0:
            raise ValidationError({'value': "La tasa de cambio debe ser un valor positivo mayor a cero."})
        
        # Evitar fechas demasiado futuristas (máximo mañana)
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)
        if self.fecha_valor > tomorrow:
            raise ValidationError({'fecha_valor': "No se puede registrar una tasa con fecha posterior a mañana."})


class EconomicIndicator(models.Model):
    INDICATOR_CHOICES = (
        ('INTERES_ACTIVA', 'Tasa de Interés Activa'),
        ('INTERES_PROM', 'Tasa de Interés Promedio'),
        ('INFLACION', 'Inflación Mensual (INPC)'),
        ('RESERVAS', 'Reservas Internacionales'),
    )
    
    name = models.CharField(max_length=100, choices=INDICATOR_CHOICES, verbose_name="Nombre del Indicador")
    value = models.DecimalField(max_digits=20, decimal_places=4, verbose_name="Valor")
    unit = models.CharField(max_length=20, default='%', help_text="Ej: %, USD, Bs.")
    fecha_referencia = models.DateField(verbose_name="Fecha del Dato")
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Indicador Económico"
        verbose_name_plural = "Indicadores Económicos"
        ordering = ['-fecha_referencia']

    def __str__(self):
        return f"{self.get_name_display()} - {self.value}{self.unit} ({self.fecha_referencia})"

class PageVisit(models.Model):
    TYPE_CHOICES = (
        ('WEB', 'Página Web (Humano)'),
        ('API', 'Consumo API'),
        ('BOT', 'Bot / Monitor'),
    )
    PLATFORM_CHOICES = (
        ('PC', 'Escritorio'),
        ('MOBILE', 'Móvil'),
        ('TABLET', 'Tablet'),
        ('UNKNOWN', 'Desconocido'),
    )
    
    path = models.CharField(max_length=255, verbose_name="Ruta")
    date = models.DateField(auto_now_add=True, verbose_name="Fecha")
    count = models.PositiveIntegerField(default=0, verbose_name="Número de Visitas")
    visitor_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='WEB', verbose_name="Tipo de Visitante")
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default='UNKNOWN', verbose_name="Plataforma")
    referer = models.CharField(max_length=500, blank=True, null=True, verbose_name="Origen (Referer)")

    class Meta:
        verbose_name = "Estadística de Visita"
        verbose_name_plural = "Estadísticas de Visitas"
        unique_together = ('path', 'date', 'visitor_type', 'platform', 'referer')
        ordering = ['-date', '-count']

    def __str__(self):
        return f"{self.path} ({self.visitor_type} - {self.platform}) - {self.date}"
