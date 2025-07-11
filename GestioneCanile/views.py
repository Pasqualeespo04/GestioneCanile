from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Canile, Cane, RegistroSanitario, Adozione, Attivita
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
import csv
import io
import random
import string

# Create your views here.

def genera_codice_tracciamento(length=8):
    """Genera un codice di tracciamento univoco per le richieste di adozione"""
    caratteri = string.ascii_uppercase + string.digits
    while True:
        codice = ''.join(random.choice(caratteri) for _ in range(length))
        # Verifica che il codice non esista già nel database
        if not Adozione.objects.filter(codice_tracciamento=codice).exists():
            return codice
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
    # Verifica se si tratta di un cane placeholder (ID da 1 a 6)
    is_placeholder = 1 <= cane_id <= 6

    if is_placeholder:
        # Definisci i dettagli dei cani placeholder (stesso dizionario usato in dettaglio_cane_placeholder)
        placeholder_dogs = {
            1: {
                'nome': 'Max',
                'razza': 'Labrador',
                'eta': 3,
                'sesso': 'Maschio',
                'peso': 30,
                'taglia': 'Grande',
                'sterilizzato': True,
                'compatibile_bambini': True,
                'compatibile_animali': True,
                'descrizione': 'Max è un labrador molto affettuoso e giocherellone.',
                'canile': 'Canile Municipale'
            },
            2: {
                'nome': 'Luna',
                'razza': 'Pastore Tedesco',
                'eta': 2,
                'sesso': 'Femmina',
                'peso': 25,
                'taglia': 'Grande',
                'sterilizzato': True,
                'compatibile_bambini': True,
                'compatibile_animali': False,
                'descrizione': 'Luna è una pastore tedesco molto intelligente e protettiva.',
                'canile': 'Canile Municipale'
            },
            3: {
                'nome': 'Rocky',
                'razza': 'Bulldog',
                'eta': 4,
                'sesso': 'Maschio',
                'peso': 20,
                'taglia': 'Media',
                'sterilizzato': True,
                'compatibile_bambini': True,
                'compatibile_animali': True,
                'descrizione': 'Rocky è un bulldog tranquillo e affettuoso.',
                'canile': 'Canile Municipale'
            },
            4: {
                'nome': 'Bella',
                'razza': 'Beagle',
                'eta': 1,
                'sesso': 'Femmina',
                'peso': 10,
                'taglia': 'Piccola',
                'sterilizzato': False,
                'compatibile_bambini': True,
                'compatibile_animali': True,
                'descrizione': 'Bella è una beagle giovane e vivace.',
                'canile': 'Canile Municipale'
            },
            5: {
                'nome': 'Charlie',
                'razza': 'Golden Retriever',
                'eta': 5,
                'sesso': 'Maschio',
                'peso': 32,
                'taglia': 'Grande',
                'sterilizzato': True,
                'compatibile_bambini': True,
                'compatibile_animali': True,
                'descrizione': 'Charlie è un golden retriever maturo e tranquillo.',
                'canile': 'Canile Municipale'
            },
            6: {
                'nome': 'Daisy',
                'razza': 'Barboncino',
                'eta': 2,
                'sesso': 'Femmina',
                'peso': 5,
                'taglia': 'Piccola',
                'sterilizzato': True,
                'compatibile_bambini': True,
                'compatibile_animali': True,
                'descrizione': 'Daisy è un barboncino toy molto vivace e affettuosa.',
                'canile': 'Canile Municipale'
            }
        }

        # Ottieni i dettagli del cane placeholder
        cane_placeholder = placeholder_dogs.get(cane_id)

        if not cane_placeholder:
            messages.warning(request, "Questo cane non esiste.")
            return redirect('cani_disponibili_foto')

        # Per i placeholder, gestiamo sia GET che POST
        if request.method == 'POST':
            # Verifica che i termini siano stati accettati
            if not request.POST.get('accetta_termini'):
                messages.error(request, "Devi accettare i termini e le condizioni per procedere con la richiesta di adozione.")
                return redirect('richiesta_adozione', cane_id=cane_id)

            # Per i placeholder, mostriamo solo un messaggio di successo senza salvare nel database
            # Generiamo comunque un codice di tracciamento per permettere all'utente di tracciare la richiesta
            codice_tracciamento = genera_codice_tracciamento()
            messages.success(request, f"La tua richiesta di adozione per {cane_placeholder['nome']} è stata inviata con successo. Il tuo codice di tracciamento è: {codice_tracciamento}. Ti contatteremo presto!")

            # Salviamo temporaneamente l'adozione in sessione per mostrarla nella pagina di conferma
            # Generiamo un URL di placeholder per la foto del cane
            placeholder_foto = f'https://placedog.net/500/280?id={cane_id}'

            request.session['adozione_placeholder'] = {
                'nome_cane': cane_placeholder['nome'],
                'razza_cane': cane_placeholder['razza'],
                'adottante_nome': request.POST.get('nome', ''),
                'adottante_cognome': request.POST.get('cognome', ''),
                'adottante_email': request.POST.get('email', ''),
                'adottante_telefono': request.POST.get('telefono', ''),
                'data_richiesta': timezone.now().strftime('%Y-%m-%d'),
                'codice_tracciamento': codice_tracciamento,
                'status': 'richiesta',
                'foto_cane': placeholder_foto
            }

            # Creiamo un'adozione reale nel database per permettere il tracciamento
            try:
                # Troviamo un cane reale disponibile o usiamo il primo disponibile
                cane_reale = Cane.objects.filter(status='disponibile').first()
                if cane_reale:
                    adozione = Adozione(
                        cane=cane_reale,
                        adottante_nome=request.POST.get('nome', ''),
                        adottante_cognome=request.POST.get('cognome', ''),
                        adottante_email=request.POST.get('email', ''),
                        adottante_telefono=request.POST.get('telefono', ''),
                        adottante_indirizzo=request.POST.get('indirizzo', ''),
                        tipo_abitazione=request.POST.get('tipo_abitazione', 'appartamento'),
                        esperienza_animali=request.POST.get('esperienza_animali', 'nessuna'),
                        presenza_bambini='presenza_bambini' in request.POST,
                        presenza_altri_animali='presenza_altri_animali' in request.POST,
                        descrizione_altri_animali=request.POST.get('descrizione_altri_animali', ''),
                        ricevi_aggiornamenti_email='ricevi_aggiornamenti_email' in request.POST,
                        ricevi_aggiornamenti_sms='ricevi_aggiornamenti_sms' in request.POST,
                        accetta_termini=True,
                        data_richiesta=timezone.now(),
                        status='richiesta',
                        note=f"Adozione placeholder per {cane_placeholder['nome']} (ID: {cane_id})",
                        codice_tracciamento=codice_tracciamento
                    )
                    adozione.save()
                    return redirect('conferma_adozione', adozione_id=adozione.id)
            except Exception as e:
                # Se qualcosa va storto, continuiamo con il redirect normale
                pass

            return redirect('cani_disponibili_foto')

        # Per i placeholder, usiamo un contesto diverso
        context = {
            'cane_placeholder': cane_placeholder,
            'placeholder_id': cane_id,
        }
        return render(request, 'GestioneCanile/richiesta_adozione_placeholder.html', context)
    else:
        # Per i cani reali, procedi come prima
        cane = get_object_or_404(Cane, id=cane_id)

        # Verifica che il cane sia disponibile per l'adozione
        if cane.status != 'disponibile':
            messages.warning(request, "Questo cane non è attualmente disponibile per l'adozione.")
            return redirect('dettaglio_cane', cane_id=cane_id)

        if request.method == 'POST':
            # Verifica che i termini siano stati accettati
            if not request.POST.get('accetta_termini'):
                messages.error(request, "Devi accettare i termini e le condizioni per procedere con la richiesta di adozione.")
                return redirect('richiesta_adozione', cane_id=cane_id)

            # Processa il form di richiesta adozione
            adozione = Adozione(
                cane=cane,
                adottante_nome=request.POST.get('nome'),
                adottante_cognome=request.POST.get('cognome'),
                adottante_email=request.POST.get('email'),
                adottante_telefono=request.POST.get('telefono'),
                adottante_indirizzo=request.POST.get('indirizzo'),
                tipo_abitazione=request.POST.get('tipo_abitazione'),
                esperienza_animali=request.POST.get('esperienza_animali'),
                presenza_bambini='presenza_bambini' in request.POST,
                presenza_altri_animali='presenza_altri_animali' in request.POST,
                descrizione_altri_animali=request.POST.get('descrizione_altri_animali', ''),
                ricevi_aggiornamenti_email='ricevi_aggiornamenti_email' in request.POST,
                ricevi_aggiornamenti_sms='ricevi_aggiornamenti_sms' in request.POST,
                accetta_termini=True,  # Se arriviamo qui, i termini sono stati accettati
                data_richiesta=timezone.now(),
                status='richiesta',
                note=request.POST.get('note', ''),
                codice_tracciamento=genera_codice_tracciamento()
            )
            adozione.save()

            # Aggiorna lo status del cane
            cane.status = 'in_adozione'
            cane.save()

            messages.success(request, f"La tua richiesta di adozione per {cane.nome} è stata inviata con successo. Il tuo codice di tracciamento è: {adozione.codice_tracciamento}. Ti contatteremo presto!")
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
    context = {}
    return render(request, 'GestioneCanile/chi_siamo.html', context)

def contatti(request):
    """Vista per la pagina dei contatti"""
    context = {}
    return render(request, 'GestioneCanile/contatti.html', context)

def traccia_adozione(request):
    """Vista per tracciare lo stato di una richiesta di adozione tramite codice"""
    adozione = None
    messaggio_errore = None
    adozione_placeholder = None

    if request.method == 'POST':
        codice = request.POST.get('codice_tracciamento', '').strip().upper()
        if codice:
            try:
                adozione = Adozione.objects.get(codice_tracciamento=codice)
            except Adozione.DoesNotExist:
                # Verifica se esiste un'adozione placeholder nella sessione
                if 'adozione_placeholder' in request.session and request.session['adozione_placeholder'].get('codice_tracciamento') == codice:
                    adozione_placeholder = request.session['adozione_placeholder']
                else:
                    messaggio_errore = "Nessuna richiesta trovata con questo codice. Verifica di aver inserito il codice correttamente."
        else:
            messaggio_errore = "Inserisci il codice di tracciamento per verificare lo stato della tua richiesta."

    context = {
        'adozione': adozione,
        'adozione_placeholder': adozione_placeholder,
        'messaggio_errore': messaggio_errore,
    }
    return render(request, 'GestioneCanile/traccia_adozione.html', context)

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

def cani_disponibili_foto(request):
    """Vista per visualizzare le foto di tutti i cani disponibili senza alcun criterio di filtro"""
    # Ottiene tutti i cani con status 'disponibile' senza applicare filtri
    cani = Cane.objects.filter(status='disponibile').order_by('-data_ingresso')

    # Se non ci sono cani disponibili, mostra comunque alcuni cani (anche con altri status)
    if not cani.exists():
        # Prendi cani con qualsiasi status, escludendo quelli già adottati
        cani = Cane.objects.exclude(status='adottato').order_by('-data_ingresso')

        # Se ancora non ci sono cani, prendi tutti i cani nel sistema
        if not cani.exists():
            cani = Cane.objects.all().order_by('-data_ingresso')

    # Paginazione
    paginator = Paginator(cani, 12)  # 12 cani per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Adotta un cane',
    }
    return render(request, 'GestioneCanile/cani_disponibili_foto.html', context)

def dettaglio_cane_placeholder(request, placeholder_id):
    """Vista per visualizzare i dettagli di un cane placeholder"""
    # Definisci i dettagli dei cani placeholder
    placeholder_dogs = {
        1: {
            'nome': 'Max',
            'razza': 'Labrador',
            'eta': 3,
            'sesso': 'Maschio',
            'peso': 30,
            'taglia': 'Grande',
            'sterilizzato': True,
            'compatibile_bambini': True,
            'compatibile_animali': True,
            'descrizione': 'Max è un labrador molto affettuoso e giocherellone. Ama correre e giocare con la palla. È molto socievole con le persone e gli altri cani. Ha bisogno di molto esercizio fisico e di una famiglia attiva che lo porti spesso a passeggio.',
            'canile': 'Canile Municipale'
        },
        2: {
            'nome': 'Luna',
            'razza': 'Pastore Tedesco',
            'eta': 2,
            'sesso': 'Femmina',
            'peso': 25,
            'taglia': 'Grande',
            'sterilizzato': True,
            'compatibile_bambini': True,
            'compatibile_animali': False,
            'descrizione': 'Luna è una pastore tedesco molto intelligente e protettiva. È molto affettuosa con la sua famiglia ma può essere diffidente con gli estranei. Ha bisogno di stimolazione mentale e di un proprietario esperto che la guidi con fermezza ma dolcezza.',
            'canile': 'Canile Municipale'
        },
        3: {
            'nome': 'Rocky',
            'razza': 'Bulldog',
            'eta': 4,
            'sesso': 'Maschio',
            'peso': 20,
            'taglia': 'Media',
            'sterilizzato': True,
            'compatibile_bambini': True,
            'compatibile_animali': True,
            'descrizione': 'Rocky è un bulldog tranquillo e affettuoso. Ama stare sul divano e ricevere coccole. Non ha bisogno di molto esercizio fisico ma ama le passeggiate tranquille. È molto paziente con i bambini e va d\'accordo con gli altri animali.',
            'canile': 'Canile Municipale'
        },
        4: {
            'nome': 'Bella',
            'razza': 'Beagle',
            'eta': 1,
            'sesso': 'Femmina',
            'peso': 10,
            'taglia': 'Piccola',
            'sterilizzato': False,
            'compatibile_bambini': True,
            'compatibile_animali': True,
            'descrizione': 'Bella è una beagle giovane e vivace. Ama esplorare e seguire le tracce con il suo naso. È molto socievole e ama giocare con i bambini e gli altri cani. Ha bisogno di un giardino recintato perché tende a seguire gli odori e potrebbe allontanarsi.',
            'canile': 'Canile Municipale'
        },
        5: {
            'nome': 'Charlie',
            'razza': 'Golden Retriever',
            'eta': 5,
            'sesso': 'Maschio',
            'peso': 32,
            'taglia': 'Grande',
            'sterilizzato': True,
            'compatibile_bambini': True,
            'compatibile_animali': True,
            'descrizione': 'Charlie è un golden retriever maturo e tranquillo. È molto affettuoso e paziente, perfetto per una famiglia con bambini. Ama nuotare e recuperare oggetti. È molto intelligente e facile da addestrare. Ha bisogno di esercizio regolare ma non eccessivo.',
            'canile': 'Canile Municipale'
        },
        6: {
            'nome': 'Daisy',
            'razza': 'Barboncino',
            'eta': 2,
            'sesso': 'Femmina',
            'peso': 5,
            'taglia': 'Piccola',
            'sterilizzato': True,
            'compatibile_bambini': True,
            'compatibile_animali': True,
            'descrizione': 'Daisy è un barboncino toy molto vivace e affettuosa. È molto intelligente e impara rapidamente i comandi. Non perde pelo, quindi è adatta anche a persone allergiche. Ama giocare e ricevere attenzioni. Ha bisogno di passeggiate regolari e di stimolazione mentale.',
            'canile': 'Canile Municipale'
        }
    }

    # Verifica che l'ID del placeholder sia valido
    if placeholder_id < 1 or placeholder_id > 6:
        messages.warning(request, "Questo cane non esiste.")
        return redirect('cani_disponibili_foto')

    # Ottieni i dettagli del cane placeholder
    cane_placeholder = placeholder_dogs[placeholder_id]

    context = {
        'cane_placeholder': cane_placeholder,
        'placeholder_id': placeholder_id,
    }
    return render(request, 'GestioneCanile/dettaglio_cane_placeholder.html', context)


def register(request):
    """
    Vista per la registrazione di un nuovo utente
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Account creato con successo! Benvenuto, {username}!')
            return redirect('home')
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
    else:
        form = UserCreationForm()

    return render(request, 'GestioneCanile/register.html', {'form': form})

def user_login(request):
    """
    Vista per il login di un utente
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Benvenuto, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Username o password non validi.')
        else:
            messages.error(request, 'Username o password non validi.')
    else:
        form = AuthenticationForm()

    return render(request, 'GestioneCanile/login.html', {'form': form})
