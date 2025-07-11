# Gestione Canile - Sistema di Gestione per Canili

## Importazione Database dei Cani

Il sistema permette di importare facilmente un database di cani tramite un file CSV. Questa funzionalità è accessibile dalla sezione amministrativa del sito.

### Come Importare i Cani

1. Accedi al sistema con le tue credenziali
2. Vai alla dashboard amministrativa
3. Seleziona "Gestione Cani" dal menu
4. Clicca su "Importa Cani" nella pagina di gestione cani
5. Nella pagina di importazione:
   - Scarica il file CSV di esempio (opzionale)
   - Prepara il tuo file CSV seguendo il formato richiesto
   - Carica il file CSV utilizzando il form
   - Clicca su "Importa Cani"

### Formato del File CSV

Il file CSV deve contenere le seguenti colonne nell'ordine indicato:

1. **Nome** - Nome del cane
2. **Razza** - Razza del cane
3. **Data di nascita** - Formato YYYY-MM-DD (può essere vuoto)
4. **Sesso** - M o F
5. **Peso** - Peso in kg (può essere vuoto)
6. **Microchip** - Numero microchip (può essere vuoto)
7. **Sterilizzato** - Si/No, Yes/No, True/False, 1/0
8. **ID Canile** - ID numerico del canile

La prima riga del file deve contenere le intestazioni delle colonne.

### Esempio di File CSV

```
Nome,Razza,Data di nascita,Sesso,Peso,Microchip,Sterilizzato,ID Canile
Rex,Pastore Tedesco,2020-05-15,M,30.5,123456789012345,Si,1
Luna,Labrador,2019-10-20,F,25.2,987654321098765,No,1
```

### Note Importanti

- I cani con numeri di microchip già presenti nel sistema verranno saltati durante l'importazione
- Assicurati che l'ID del canile sia corretto e corrisponda a un canile esistente nel sistema
- I campi data di nascita, peso e microchip possono essere lasciati vuoti
- Il campo sterilizzato accetta vari formati (Si/No, Yes/No, True/False, 1/0)

Per qualsiasi problema durante l'importazione, controlla i messaggi di errore visualizzati nella pagina.