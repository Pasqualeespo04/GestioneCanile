from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Canile, Cane, RegistroSanitario, Adozione, Attivita
from django.utils import timezone
import csv
import io

# Create your views here.
def home(request):
    """Vista per la homepage del sito"""
    cani_disponibili = Cane.objects.filter(status='disponibile').order_by('-data_ingresso')[:6]
    canili = Canile.objects.all()

    # Statistiche per la homepage
    total_cani_disponibili = Cane.objects.filter(status='disponibile').count()
    total_cani = Cane.objects.count()  # Totale cani nel sistema
    adozioni_completate = Adozione.objects.filter(status='completata').count()
    adozioni_in_corso = Adozione.objects.exclude(status__in=['completata', 'rifiutata']).count()

    context = {
        'cani_disponibili': cani_disponibili,
        'canili': canili,
        'total_cani_disponibili': total_cani_disponibili,
        'total_cani': total_cani,
        'adozioni_completate': adozioni_completate,
        'adozioni_in_corso': adozioni_in_corso,
    }
    return render(request, 'GestioneCanile/home.html', context)

def lista_cani(request):
    """Vista per visualizzare tutti i cani disponibili per l'adozione"""
    query = request.GET.get('q', '')
    canile_id = request.GET.get('canile', '')
    cane_id = request.GET.get('cane', '')
    taglia = request.GET.get('taglia', '')
    sesso = request.GET.get('sesso', '')
    eta_min = request.GET.get('eta_min', '')
    eta_max = request.GET.get('eta_max', '')
    compatibile_bambini = request.GET.get('compatibile_bambini', '')
    compatibile_animali = request.GET.get('compatibile_animali', '')

    cani = Cane.objects.filter(status='disponibile')

    # Tutti i cani disponibili per il dropdown
    cani_disponibili = Cane.objects.filter(status='disponibile').order_by('nome')

    if query:
        cani = cani.filter(
            Q(nome__icontains=query) | 
            Q(razza__icontains=query) | 
            Q(descrizione__icontains=query)
        )

    if canile_id:
        cani = cani.filter(canile_id=canile_id)

    if cane_id:
        cani = cani.filter(id=cane_id)

    # Filtri aggiuntivi
    if taglia:
        cani = cani.filter(taglia=taglia)

    if sesso:
        cani = cani.filter(sesso=sesso)

    # Filtro per età
    import datetime
    from django.utils import timezone

    if eta_min and eta_min.isdigit():
        # Calcola la data di nascita massima per l'età minima
        today = timezone.now().date()
        max_birth_date = datetime.date(today.year - int(eta_min), today.month, today.day)
        cani = cani.filter(data_nascita__lte=max_birth_date)

    if eta_max and eta_max.isdigit():
        # Calcola la data di nascita minima per l'età massima
        today = timezone.now().date()
        min_birth_date = datetime.date(today.year - int(eta_max) - 1, today.month, today.day)
        cani = cani.filter(data_nascita__gt=min_birth_date)

    # Filtri per compatibilità
    if compatibile_bambini:
        cani = cani.filter(compatibile_bambini=True)

    if compatibile_animali:
        cani = cani.filter(compatibile_animali=True)

    # Ordinamento
    sort_by = request.GET.get('sort', '-data_ingresso')
    cani = cani.order_by(sort_by)

    # Paginazione
    paginator = Paginator(cani, 12)  # 12 cani per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    canili = Canile.objects.all()

    context = {
        'page_obj': page_obj,
        'query': query,
        'canile_id': canile_id,
        'cane_id': cane_id,
        'taglia': taglia,
        'sesso': sesso,
        'eta_min': eta_min,
        'eta_max': eta_max,
        'compatibile_bambini': compatibile_bambini,
        'compatibile_animali': compatibile_animali,
        'canili': canili,
        'cani_disponibili': cani_disponibili,
        'sort_by': sort_by,
    }
    return render(request, 'GestioneCanile/lista_cani.html', context)

def dettaglio_cane(request, cane_id):
    """Vista per visualizzare i dettagli di un cane specifico"""
    cane = get_object_or_404(Cane, id=cane_id)

    # Se il cane non è disponibile per l'adozione, mostra solo se l'utente è autenticato
    if cane.status != 'disponibile' and not request.user.is_authenticated:
        messages.warning(request, "Questo cane non è attualmente disponibile per l'adozione.")
        return redirect('lista_cani')

    context = {
        'cane': cane,
    }
    return render(request, 'GestioneCanile/dettaglio_cane.html', context)

def richiesta_adozione(request, cane_id):
    """Vista per richiedere l'adozione di un cane"""
    cane = get_object_or_404(Cane, id=cane_id)

    # Verifica che il cane sia disponibile per l'adozione
    if cane.status != 'disponibile':
        messages.warning(request, "Questo cane non è attualmente disponibile per l'adozione.")
        return redirect('dettaglio_cane', cane_id=cane_id)

    if request.method == 'POST':
        # Processa il form di richiesta adozione
        adozione = Adozione(
            cane=cane,
            adottante_nome=request.POST.get('nome'),
            adottante_cognome=request.POST.get('cognome'),
            adottante_email=request.POST.get('email'),
            adottante_telefono=request.POST.get('telefono'),
            adottante_indirizzo=request.POST.get('indirizzo'),
            data_richiesta=timezone.now(),
            status='richiesta',
            note=request.POST.get('note', '')
        )
        adozione.save()

        # Aggiorna lo status del cane
        cane.status = 'in_adozione'
        cane.save()

        messages.success(request, f"La tua richiesta di adozione per {cane.nome} è stata inviata con successo. Ti contatteremo presto!")
        return redirect('conferma_adozione', adozione_id=adozione.id)

    context = {
        'cane': cane,
    }
    return render(request, 'GestioneCanile/richiesta_adozione.html', context)

def conferma_adozione(request, adozione_id):
    """Vista per confermare la richiesta di adozione"""
    adozione = get_object_or_404(Adozione, id=adozione_id)

    context = {
        'adozione': adozione,
    }
    return render(request, 'GestioneCanile/conferma_adozione.html', context)

def chi_siamo(request):
    """Vista per la pagina 'Chi Siamo'"""
    canili = Canile.objects.all()

    context = {
        'canili': canili,
    }
    return render(request, 'GestioneCanile/chi_siamo.html', context)

def contatti(request):
    """Vista per la pagina dei contatti"""
    canili = Canile.objects.all()

    context = {
        'canili': canili,
    }
    return render(request, 'GestioneCanile/contatti.html', context)

# Viste per l'area amministrativa (riservate agli utenti autenticati)
@login_required
def dashboard(request):
    """Dashboard per gli operatori del canile"""
    # Statistiche generali
    cani_totali = Cane.objects.count()
    cani_disponibili = Cane.objects.filter(status='disponibile').count()
    adozioni_in_corso = Adozione.objects.filter(status__in=['richiesta', 'in_valutazione', 'approvata']).count()
    adozioni_completate = Adozione.objects.filter(status='completata').count()

    # Cani che necessitano di attenzione (controlli sanitari imminenti)
    oggi = timezone.now().date()
    controlli_imminenti = RegistroSanitario.objects.filter(
        prossimo_controllo__isnull=False,
        prossimo_controllo__lte=oggi + timezone.timedelta(days=7)
    ).order_by('prossimo_controllo')

    # Ultime adozioni
    ultime_adozioni = Adozione.objects.all().order_by('-data_richiesta')[:5]

    # Attività recenti
    attivita_recenti = Attivita.objects.filter(
        data__gte=oggi - timezone.timedelta(days=7)
    ).order_by('-data', '-ora_inizio')

    context = {
        'cani_totali': cani_totali,
        'cani_disponibili': cani_disponibili,
        'adozioni_in_corso': adozioni_in_corso,
        'adozioni_completate': adozioni_completate,
        'controlli_imminenti': controlli_imminenti,
        'ultime_adozioni': ultime_adozioni,
        'attivita_recenti': attivita_recenti,
    }
    return render(request, 'GestioneCanile/dashboard.html', context)

@login_required
def gestione_cani(request):
    """Vista per la gestione dei cani (lista completa)"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    canile_id = request.GET.get('canile', '')

    cani = Cane.objects.all()

    if query:
        cani = cani.filter(
            Q(nome__icontains=query) | 
            Q(razza__icontains=query) | 
            Q(microchip__icontains=query)
        )

    if status:
        cani = cani.filter(status=status)

    if canile_id:
        cani = cani.filter(canile_id=canile_id)

    # Ordinamento
    sort_by = request.GET.get('sort', '-data_ingresso')
    cani = cani.order_by(sort_by)

    # Paginazione
    paginator = Paginator(cani, 20)  # 20 cani per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    canili = Canile.objects.all()

    context = {
        'page_obj': page_obj,
        'query': query,
        'status': status,
        'canile_id': canile_id,
        'canili': canili,
        'sort_by': sort_by,
    }
    return render(request, 'GestioneCanile/gestione_cani.html', context)

@login_required
def gestione_adozioni(request):
    """Vista per la gestione delle adozioni"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')

    adozioni = Adozione.objects.all()

    if query:
        adozioni = adozioni.filter(
            Q(cane__nome__icontains=query) | 
            Q(adottante_cognome__icontains=query) | 
            Q(adottante_nome__icontains=query) | 
            Q(adottante_email__icontains=query)
        )

    if status:
        adozioni = adozioni.filter(status=status)

    # Ordinamento
    sort_by = request.GET.get('sort', '-data_richiesta')
    adozioni = adozioni.order_by(sort_by)

    # Paginazione
    paginator = Paginator(adozioni, 20)  # 20 adozioni per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'status': status,
        'sort_by': sort_by,
    }
    return render(request, 'GestioneCanile/gestione_adozioni.html', context)

@login_required
def registro_sanitario(request, cane_id):
    """Vista per visualizzare e aggiungere registri sanitari per un cane specifico"""
    cane = get_object_or_404(Cane, id=cane_id)
    registri = RegistroSanitario.objects.filter(cane=cane).order_by('-data')

    context = {
        'cane': cane,
        'registri': registri,
    }
    return render(request, 'GestioneCanile/registro_sanitario.html', context)

@login_required
def import_cani(request):
    """Vista per importare cani da un file CSV"""
    canili = Canile.objects.all()

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        # Verifica che sia un file CSV
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Il file deve essere in formato CSV.')
            return redirect('import_cani')

        # Leggi il file CSV
        try:
            # Decodifica il file
            file_data = csv_file.read().decode('utf-8')
            csv_data = csv.reader(io.StringIO(file_data), delimiter=',')

            # Salta l'intestazione
            next(csv_data)

            # Contatori per i messaggi
            cani_importati = 0
            cani_saltati = 0

            for row in csv_data:
                if len(row) < 8:  # Verifica che ci siano abbastanza colonne
                    cani_saltati += 1
                    continue

                nome = row[0]
                razza = row[1]
                data_nascita = row[2] if row[2] else None
                sesso = row[3]
                peso = row[4] if row[4] else None
                microchip = row[5] if row[5] else None
                sterilizzato = True if row[6].lower() in ['si', 'sì', 'yes', 'true', '1'] else False
                canile_id = int(row[7])

                # Verifica che il canile esista
                try:
                    canile = Canile.objects.get(id=canile_id)
                except Canile.DoesNotExist:
                    cani_saltati += 1
                    continue

                # Verifica che il microchip non esista già
                if microchip and Cane.objects.filter(microchip=microchip).exists():
                    cani_saltati += 1
                    continue

                # Crea il nuovo cane
                cane = Cane(
                    nome=nome,
                    razza=razza,
                    data_nascita=data_nascita if data_nascita else None,
                    sesso=sesso,
                    peso=peso if peso else None,
                    microchip=microchip,
                    sterilizzato=sterilizzato,
                    canile=canile,
                    status='disponibile'
                )

                cane.save()
                cani_importati += 1

            if cani_importati > 0:
                messages.success(request, f'Importazione completata: {cani_importati} cani importati, {cani_saltati} cani saltati.')
            else:
                messages.warning(request, f'Nessun cane importato. {cani_saltati} cani saltati.')

        except Exception as e:
            messages.error(request, f'Errore durante l\'importazione: {str(e)}')

    context = {
        'canili': canili
    }
    return render(request, 'GestioneCanile/import_cani.html', context)
