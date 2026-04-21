from django.contrib import admin
from django.utils.html import format_html
from .models import ExchangeRate, EconomicIndicator

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
