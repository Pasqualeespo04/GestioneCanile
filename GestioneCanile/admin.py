from django.contrib import admin
from .models import Canile, Cane, RegistroSanitario, Adozione, Attivita

# Register your models here.
@admin.register(Canile)
class CanileAdmin(admin.ModelAdmin):
    list_display = ('nome', 'citta', 'telefono', 'capacita_massima')
    search_fields = ('nome', 'citta')
    list_filter = ('citta',)

@admin.register(Cane)
class CaneAdmin(admin.ModelAdmin):
    list_display = ('nome', 'razza', 'sesso', 'data_ingresso', 'status', 'canile', 'microchip')
    list_filter = ('status', 'canile', 'sesso', 'sterilizzato')
    search_fields = ('nome', 'razza', 'microchip')
    date_hierarchy = 'data_ingresso'
    readonly_fields = ('eta',)
    fieldsets = (
        ('Informazioni Principali', {
            'fields': ('nome', 'razza', 'data_nascita', 'sesso', 'canile')
        }),
        ('Dettagli Fisici', {
            'fields': ('peso', 'sterilizzato', 'foto')
        }),
        ('Informazioni Amministrative', {
            'fields': ('microchip', 'data_ingresso', 'status', 'descrizione')
        }),
    )

@admin.register(RegistroSanitario)
class RegistroSanitarioAdmin(admin.ModelAdmin):
    list_display = ('cane', 'data', 'tipo_intervento', 'veterinario', 'prossimo_controllo')
    list_filter = ('data', 'tipo_intervento', 'veterinario')
    search_fields = ('cane__nome', 'tipo_intervento', 'veterinario')
    date_hierarchy = 'data'
    autocomplete_fields = ('cane',)

@admin.register(Adozione)
class AdozioneAdmin(admin.ModelAdmin):
    list_display = ('cane', 'adottante_cognome', 'adottante_nome', 'data_richiesta', 'status')
    list_filter = ('status', 'data_richiesta')
    search_fields = ('cane__nome', 'adottante_cognome', 'adottante_nome', 'adottante_email')
    date_hierarchy = 'data_richiesta'
    autocomplete_fields = ('cane', 'operatore')
    fieldsets = (
        ('Informazioni Cane', {
            'fields': ('cane',)
        }),
        ('Informazioni Adottante', {
            'fields': ('adottante_nome', 'adottante_cognome', 'adottante_email', 'adottante_telefono', 'adottante_indirizzo')
        }),
        ('Stato Adozione', {
            'fields': ('status', 'data_richiesta', 'data_adozione', 'operatore', 'note')
        }),
    )

@admin.register(Attivita)
class AttivitaAdmin(admin.ModelAdmin):
    list_display = ('cane', 'tipo', 'data', 'ora_inizio', 'ora_fine', 'operatore')
    list_filter = ('tipo', 'data', 'operatore')
    search_fields = ('cane__nome', 'note')
    date_hierarchy = 'data'
    autocomplete_fields = ('cane', 'operatore')
