from django.urls import path
from . import views

urlpatterns = [
    # Public-facing URLs
    path('', views.home, name='home'),
    path('cani/', views.lista_cani, name='lista_cani'),
    path('cani/<int:cane_id>/', views.dettaglio_cane, name='dettaglio_cane'),
    path('cani/<int:cane_id>/adozione/', views.richiesta_adozione, name='richiesta_adozione'),
    path('adozione/<int:adozione_id>/conferma/', views.conferma_adozione, name='conferma_adozione'),
    path('chi-siamo/', views.chi_siamo, name='chi_siamo'),
    path('contatti/', views.contatti, name='contatti'),

    # Admin/operator URLs (protected with login_required)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('gestione/cani/', views.gestione_cani, name='gestione_cani'),
    path('gestione/cani/import/', views.import_cani, name='import_cani'),
    path('gestione/adozioni/', views.gestione_adozioni, name='gestione_adozioni'),
    path('gestione/cani/<int:cane_id>/registro-sanitario/', views.registro_sanitario, name='registro_sanitario'),
]
