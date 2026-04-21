from django.contrib import admin
from django.utils.html import format_html
from .models import ExchangeRate, EconomicIndicator, PageVisit

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('source_badge', 'currency_label', 'value_formatted', 'fecha_valor', 'is_active', 'fetched_at_formatted')
    list_filter = ('source', 'currency', 'is_active', 'fecha_valor')
    search_fields = ('currency', 'fecha_valor')
    ordering = ('-fecha_valor', '-fetched_at')
    
    # Agrupamos los campos para que el formulario manual sea más limpio
    fieldsets = (
        ('Información de la Tasa', {
            'fields': (('source', 'currency'), 'value', 'fecha_valor')
        }),
        ('Estado y Origen', {
            'fields': ('is_active', 'source_url'),
            'classes': ('collapse',) # Por defecto esto se puede ocultar
        }),
    )

    def source_badge(self, obj):
        colors = {
            'BCV': '#28a745',
            'PARALELO': '#dc3545',
            'BINANCE': '#ffc107'
        }
        color = colors.get(obj.source, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8em;">{}</span>',
            color, obj.get_source_display()
        )
    source_badge.short_description = "Fuente"

    def currency_label(self, obj):
        return format_html('<strong>{}</strong>', obj.currency)
    currency_label.short_description = "Moneda"

    def value_formatted(self, obj):
        val = "{:,.4f}".format(obj.value)
        return format_html('<span style="font-family: monospace; font-size: 1.1em;">{}</span>', val)
    value_formatted.short_description = "Valor (VED)"

    def fetched_at_formatted(self, obj):
        return obj.fetched_at.strftime("%d/%m/%Y %H:%M")
    fetched_at_formatted.short_description = "Capturado el"

    # Forzar la validación del modelo al guardar en el Admin
    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)

@admin.register(EconomicIndicator)
class EconomicIndicatorAdmin(admin.ModelAdmin):
    list_display = ('indicator_badge', 'value_formatted', 'fecha_referencia', 'fetched_at')
    list_filter = ('name', 'fecha_referencia')
    search_fields = ('name',)

    def indicator_badge(self, obj):
        colors = {
            'INFLACION': '#dc3545',
            'INTERES_ACTIVA': '#007bff',
            'INTERES_PROM': '#17a2b8',
            'RESERVAS': '#28a745'
        }
        color = colors.get(obj.name, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8em;">{}</span>',
            color, obj.get_name_display()
        )
    indicator_badge.short_description = "Indicador"

    def value_formatted(self, obj):
        return format_html('<strong>{} {}</strong>', obj.value, obj.unit)
    value_formatted.short_description = "Valor Actual"

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('path_highlight', 'visitor_type_badge', 'date', 'count_badge', 'is_today')
    list_filter = ('visitor_type', 'date', 'path')
    date_hierarchy = 'date'
    change_list_template = 'admin/bcv_service/pagevisit/change_list.html'
    
    def path_highlight(self, obj):
        return format_html('<code style="color: #e83e8c; font-weight: bold;">{}</code>', obj.path)
    path_highlight.short_description = "Ruta"

    def visitor_type_badge(self, obj):
        colors = {'WEB': '#0d6efd', 'API': '#28a745', 'BOT': '#6c757d'}
        color = colors.get(obj.visitor_type, '#000')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: bold;">{}</span>',
            color, obj.get_visitor_type_display()
        )
    visitor_type_badge.short_description = "Tipo"

    def count_badge(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 2px 8px; display: inline-block; font-weight: bold;">{}</div>',
            obj.count
        )
    count_badge.short_description = "Visitas"

    def is_today(self, obj):
        from django.utils import timezone
        return obj.date == timezone.now().date()
    is_today.boolean = True
    is_today.short_description = "¿Hoy?"

    def changelist_view(self, request, extra_context=None):
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Sum, Count
        import json
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Resumen de hoy (SOLO HUMANOS Y API, EXCLUYENDO BOTS)
        today_qs = PageVisit.objects.filter(date=today).exclude(visitor_type='BOT')
        total_today = today_qs.aggregate(Sum('count'))['count__sum'] or 0
        total_api = today_qs.filter(visitor_type='API').aggregate(Sum('count'))['count__sum'] or 0
        total_web = today_qs.filter(visitor_type='WEB').aggregate(Sum('count'))['count__sum'] or 0
        
        total_yesterday = PageVisit.objects.filter(date=yesterday).exclude(visitor_type='BOT').aggregate(Sum('count'))['count__sum'] or 0
        
        # Comparativa vs ayer
        diff = total_today - total_yesterday
        pct_diff = 0
        if total_yesterday > 0:
            pct_diff = round((diff / total_yesterday) * 100, 1)
        
        # Top 5 Rutas (Excluyendo bots y filtrando rutas comunes de sistema)
        month_ago = today - timedelta(days=30)
        top_paths = PageVisit.objects.filter(date__gte=month_ago)\
            .exclude(visitor_type='BOT')\
            .values('path')\
            .annotate(total=Sum('count'))\
            .order_by('-total')[:5]
            
        # Desglose Plataformas (Excluyendo bots para ver usuarios reales)
        platforms = PageVisit.objects.exclude(visitor_type='BOT').values('platform').annotate(total=Sum('count'))
        platform_labels = [p['platform'] for p in platforms]
        platform_values = [p['total'] for p in platforms]
        
        # Datos para gráfico de líneas (7 días, excluyendo bots)
        labels = []
        api_data = []
        web_data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime('%d/%m'))
            day_qs = PageVisit.objects.filter(date=day).exclude(visitor_type='BOT')
            api_data.append(day_qs.filter(visitor_type='API').aggregate(Sum('count'))['count__sum'] or 0)
            web_data.append(day_qs.filter(visitor_type='WEB').aggregate(Sum('count'))['count__sum'] or 0)
            
        extra_context = extra_context or {}
        extra_context['summary'] = {
            'total_today': total_today,
            'total_api': total_api,
            'total_web': total_web,
            'api_pct': round((total_api / total_today * 100), 1) if total_today > 0 else 0,
            'web_pct': round((total_web / total_today * 100), 1) if total_today > 0 else 0,
            'today_vs_yesterday': diff,
            'today_vs_yesterday_pct': pct_diff,
            'total_rates': ExchangeRate.objects.count(),
            'top_paths': top_paths,
        }
        extra_context['chart_data_json'] = json.dumps({
            'labels': labels,
            'api_data': api_data,
            'web_data': web_data,
        })
        extra_context['platform_data_json'] = json.dumps({
            'labels': platform_labels,
            'values': platform_values,
        })
        
        return super().changelist_view(request, extra_context=extra_context)
