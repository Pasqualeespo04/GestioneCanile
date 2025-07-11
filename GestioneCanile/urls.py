from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Public-facing URLs
    path('', views.home, name='home'),
    path('cani/', views.lista_cani, name='lista_cani'),
    path('cani/foto/', views.cani_disponibili_foto, name='cani_disponibili_foto'),
    path('cani/<int:cane_id>/', views.dettaglio_cane, name='dettaglio_cane'),
    path('cani/placeholder/<int:placeholder_id>/', views.dettaglio_cane_placeholder, name='dettaglio_cane_placeholder'),
    path('cani/<int:cane_id>/adozione/', views.richiesta_adozione, name='richiesta_adozione'),
    path('adozione/<int:adozione_id>/conferma/', views.conferma_adozione, name='conferma_adozione'),
    path('adozione/traccia/', views.traccia_adozione, name='traccia_adozione'),
    path('chi-siamo/', views.chi_siamo, name='chi_siamo'),
    path('contatti/', views.contatti, name='contatti'),

    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # Admin/operator URLs (protected with login_required)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('gestione/cani/', views.gestione_cani, name='gestione_cani'),
    path('gestione/cani/import/', views.import_cani, name='import_cani'),
    path('gestione/adozioni/', views.gestione_adozioni, name='gestione_adozioni'),
    path('gestione/cani/<int:cane_id>/registro-sanitario/', views.registro_sanitario, name='registro_sanitario'),
]
