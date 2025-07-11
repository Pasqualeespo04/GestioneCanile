from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Canile(models.Model):
    nome = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=200)
    citta = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    capacita_massima = models.IntegerField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Canili"

class Cane(models.Model):
    SESSO_CHOICES = [
        ('M', 'Maschio'),
        ('F', 'Femmina'),
    ]

    STATUS_CHOICES = [
        ('disponibile', 'Disponibile per adozione'),
        ('in_adozione', 'In processo di adozione'),
        ('adottato', 'Adottato'),
        ('in_cura', 'In cura'),
        ('non_adottabile', 'Non adottabile'),
    ]

    TAGLIA_CHOICES = [
        ('piccola', 'Piccola'),
        ('media', 'Media'),
        ('grande', 'Grande'),
        ('molto_grande', 'Molto grande'),
    ]

    nome = models.CharField(max_length=100)
    razza = models.CharField(max_length=100)
    data_nascita = models.DateField(null=True, blank=True)
    data_ingresso = models.DateField(default=timezone.now)
    sesso = models.CharField(max_length=1, choices=SESSO_CHOICES)
    taglia = models.CharField(max_length=20, choices=TAGLIA_CHOICES, null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    microchip = models.CharField(max_length=15, unique=True, null=True, blank=True)
    sterilizzato = models.BooleanField(default=False)
    compatibile_bambini = models.BooleanField(default=True, help_text="Compatibile con bambini")
    compatibile_animali = models.BooleanField(default=True, help_text="Compatibile con altri animali")
    descrizione = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponibile')
    canile = models.ForeignKey(Canile, on_delete=models.CASCADE, related_name='cani')
    foto = models.ImageField(upload_to='cani_foto/', null=True, blank=True)

    def eta(self):
        if self.data_nascita:
            today = timezone.now().date()
            return today.year - self.data_nascita.year - ((today.month, today.day) < (self.data_nascita.month, self.data_nascita.day))
        return None

    def __str__(self):
        return f"{self.nome} - {self.razza}"

    class Meta:
        verbose_name_plural = "Cani"

class RegistroSanitario(models.Model):
    cane = models.ForeignKey(Cane, on_delete=models.CASCADE, related_name='registri_sanitari')
    data = models.DateField(default=timezone.now)
    tipo_intervento = models.CharField(max_length=100)
    descrizione = models.TextField()
    veterinario = models.CharField(max_length=100)
    farmaci_prescritti = models.TextField(blank=True)
    prossimo_controllo = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.cane.nome} - {self.tipo_intervento} - {self.data}"

    class Meta:
        verbose_name_plural = "Registri Sanitari"
        ordering = ['-data']

class Adozione(models.Model):
    STATUS_CHOICES = [
        ('richiesta', 'Richiesta'),
        ('in_valutazione', 'In valutazione'),
        ('approvata', 'Approvata'),
        ('completata', 'Completata'),
        ('rifiutata', 'Rifiutata'),
    ]

    TIPO_ABITAZIONE_CHOICES = [
        ('appartamento', 'Appartamento'),
        ('casa_giardino', 'Casa con giardino'),
        ('casa_rurale', 'Casa rurale/fattoria'),
        ('altro', 'Altro'),
    ]

    ESPERIENZA_CHOICES = [
        ('nessuna', 'Nessuna esperienza precedente'),
        ('poca', 'Poca esperienza'),
        ('media', 'Media esperienza'),
        ('molta', 'Molta esperienza'),
    ]

    codice_tracciamento = models.CharField(max_length=10, unique=True, blank=True, null=True, help_text="Codice univoco per tracciare la richiesta di adozione")
    cane = models.ForeignKey(Cane, on_delete=models.CASCADE, related_name='adozioni')
    adottante_nome = models.CharField(max_length=100)
    adottante_cognome = models.CharField(max_length=100)
    adottante_email = models.EmailField()
    adottante_telefono = models.CharField(max_length=20)
    adottante_indirizzo = models.CharField(max_length=200)
    tipo_abitazione = models.CharField(max_length=20, choices=TIPO_ABITAZIONE_CHOICES, default='appartamento')
    esperienza_animali = models.CharField(max_length=20, choices=ESPERIENZA_CHOICES, default='nessuna')
    presenza_bambini = models.BooleanField(default=False)
    presenza_altri_animali = models.BooleanField(default=False)
    descrizione_altri_animali = models.TextField(blank=True)
    ricevi_aggiornamenti_email = models.BooleanField(default=False)
    ricevi_aggiornamenti_sms = models.BooleanField(default=False)
    accetta_termini = models.BooleanField(default=False)
    data_richiesta = models.DateField(default=timezone.now)
    data_adozione = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='richiesta')
    note = models.TextField(blank=True)
    operatore = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='adozioni_gestite')

    def __str__(self):
        return f"{self.adottante_cognome} {self.adottante_nome} - {self.cane.nome} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        # Aggiorna lo status del cane quando l'adozione viene completata
        if self.status == 'completata' and self.data_adozione:
            self.cane.status = 'adottato'
            self.cane.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Adozioni"
        ordering = ['-data_richiesta']

class Attivita(models.Model):
    TIPO_CHOICES = [
        ('passeggiata', 'Passeggiata'),
        ('gioco', 'Sessione di gioco'),
        ('addestramento', 'Addestramento'),
        ('visita', 'Visita potenziale adottante'),
        ('altro', 'Altro'),
    ]

    cane = models.ForeignKey(Cane, on_delete=models.CASCADE, related_name='attivita')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data = models.DateField(default=timezone.now)
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField(null=True, blank=True)
    operatore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attivita_svolte')
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.cane.nome} - {self.get_tipo_display()} - {self.data}"

    class Meta:
        verbose_name_plural = "Attività"
        ordering = ['-data', '-ora_inizio']
