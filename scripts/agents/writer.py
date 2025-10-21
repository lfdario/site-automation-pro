import os
from openai import OpenAI

def _template_body(title):
    return f"""## Introduzione
In questa guida pratica su **{title}** trovi una procedura affidabile, verifiche rapide e soluzioni ai problemi più comuni.
La guida è pensata per utenti alle prime armi ma utile anche a chi è più esperto.

## Cosa imparerai
- Procedura passo-passo chiara
- Controlli e verifiche per non perdere dati
- Errori tipici e come risolverli
- Domande frequenti (FAQ)

## Prerequisiti
- Connessione internet stabile
- Account aggiornato e spazio libero sufficiente
- Permessi di amministratore sul dispositivo

## Procedura passo-passo
### 1) Preparazione
1. Aggiorna il sistema all’ultima versione disponibile.
2. Esegui un backup rapido dei file importanti.
3. Chiudi app non necessarie per evitare conflitti.

### 2) Configurazione iniziale
1. Apri le impostazioni pertinenti.
2. Verifica le opzioni consigliate in questa guida.
3. Applica le modifiche e conferma con “OK”.

### 3) Esecuzione
1. Segui le schermate e non saltare i passaggi.
2. Se compare un avviso, leggi il testo e procedi con cautela.
3. Attendi la fine del processo prima di chiudere l’app.

### 4) Verifica finale
- Controlla che la funzione attivata lavori come previsto.
- Se noti rallentamenti, riavvia il dispositivo.
- Ripeti il controllo dopo 24h.

## Ottimizzazioni consigliate
- Pianifica un controllo automatico settimanale.
- Mantieni sempre spazio libero > 15%.
- Aggiorna driver/app quando disponibili.

## Errori comuni e soluzioni
- **L’app si blocca** → Riavvia e ripeti la procedura; disattiva temporaneamente antivirus.
- **Operazione troppo lenta** → Verifica spazio libero e chiudi programmi in background.
- **Impostazioni non salvate** → Esegui come amministratore e riprova.

## Checklist finale
- [ ] Hai eseguito il backup?
- [ ] Hai seguito i passaggi nell’ordine?
- [ ] Hai verificato il risultato finale?

## FAQ
**Posso annullare senza rischi?**  
Sì, segui la sezione “Verifica finale” e torna alla configurazione precedente.

**Quanto tempo richiede?**  
In media 10–20 minuti, dipende dal dispositivo.

**È compatibile con versioni precedenti?**  
Nella maggior parte dei casi sì; se incontri problemi, prova gli step nella sezione “Errori comuni”.
"""

def generate_article(title, keywords, model='gpt-4o-mini', min_words=1500, max_words=2200, tone='chiaro e pratico'):
    api_key = os.environ.get('OPENAI_API_KEY','').strip()
    if not api_key:
        return _template_body(title), None
    try:
        client = OpenAI(api_key=api_key)
        sys_prompt = (
            f"Sei un redattore tecnico italiano. Scrivi articoli autorevoli e pratici. "
            f"Stile {tone}. Lunghezza {min_words}-{max_words} parole. "
            "Usa H2/H3, liste puntate, esempi, e 4-6 FAQ concise. "
            "Inserisci una checklist finale. Scrivi in italiano naturale."
        )
        user_prompt = (
            f"Titolo: {title}\n"
            f"Parole chiave: {', '.join(keywords)}\n"
            "Scrivi un articolo completo per un blog italiano. "
            "Evita sensazionalismi. Includi passaggi numerati, note di compatibilità (Windows/macOS/Android/iOS se pertinenti), "
            "errori comuni e soluzioni. Non inventare dati non verificabili."
        )
        resp = client.responses.create(
            model=model,
            input=[{"role":"system","content":sys_prompt},
                   {"role":"user","content":user_prompt}],
            temperature=0.7
        )
        body = getattr(resp, "output_text", "") or _template_body(title)
        schema = {
            "@context":"https://schema.org","@type":"FAQPage",
            "mainEntity":[
                {"@type":"Question","name":"Quali sono i passaggi principali?","acceptedAnswer":{"@type":"Answer","text":"Segui i passaggi descritti."}},
                {"@type":"Question","name":"Quanto tempo richiede?","acceptedAnswer":{"@type":"Answer","text":"In media 10–20 minuti, dipende dal dispositivo."}}
            ]
        }
        return body, schema
    except Exception as e:
        print("OpenAI fallback:", repr(e))
        return _template_body(title), None
