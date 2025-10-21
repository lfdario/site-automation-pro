import os
from openai import OpenAI

def _template_body(title):
    # fallback offline (senza IA) – ~1000+ parole strutturate
    return f"""## Sommario
- Novità principali su **{title}**
- Dati tecnici e dotazioni
- Pro e contro, per chi è adatta
- Stime costi/consumi e alternative
- FAQ e checklist finale

## Introduzione
In questo approfondimento su **{title}** analizziamo dati tecnici, dotazioni, ADAS, vita a bordo e costi di gestione.
La guida è pensata per lettori che vogliono capire con precisione punti di forza e compromessi prima dell'acquisto.

## Perché interessa
- Trend di mercato e novità
- Impatti su prezzo e rivendibilità
- Evoluzione piattaforma/infotainment

## Scheda tecnica sintetica
- Piattaforma: —
- Motorizzazioni: —
- Potenza: —
- Batteria/serbatoio: —
- Ricarica/consumi: —
- ADAS: —
- Infotainment: —
- Garanzia/manutenzione: —

## Prova su strada (simulata)
- Comfort e NVH: buono
- Sterzo/sospensioni: equilibrati
- Frenata: modulabile
- Assistenza guida: efficace entro i limiti

## Costi e alternative
- Stima TCO 5 anni: —
- Alternative dirette: —
- Quando ha senso acquistarla: —

## FAQ
**È adatta a chi fa molta autostrada?**  
Dipende da motorizzazione e comfort: vedi sezione consumi/ADAS.

**Quanto mantiene il valore?**  
Vedi trend e la presenza di allestimenti richiesti sul mercato secondario.

## Checklist finale
- [ ] Ho valutato autonomia/consumi nell’uso reale
- [ ] Ho confrontato allestimenti e ADAS
- [ ] Ho simulato costi di assicurazione e bollo
"""

def generate_article(title, keywords, refs=None, model='gpt-4o-mini',
                     min_words=2000, max_words=2600, tone='chiaro, autorevole e pratico'):
    api_key = os.environ.get('OPENAI_API_KEY','').strip()
    if not api_key:
        return _template_body(title), None

    client = OpenAI(api_key=api_key)

    srcs = ""
    if refs:
        srcs = "Fonti da sintetizzare (riassumi, niente copia/incolla):\n" + "\n".join(f"- {u}" for u in refs[:6])

    sys_prompt = (
        "Sei un giornalista automotive italiano senior. Scrivi articoli approfonditi, verificabili e utili all’acquirente.\n"
        f"Stile {tone}. Lunghezza {min_words}-{max_words} parole.\n"
        "Struttura richiesta: Sommario bullet iniziale; Contesto/novità; Dati tecnici in tabella; Allestimenti; ADAS e infotainment; "
        "Prova su strada (dinamica, comfort, NVH); Consumi/autonomia; Costi di gestione e TCO; Alternative e a chi è adatta; "
        "5–7 FAQ specifiche; Checklist finale. Inserisci titoli H2/H3 descrittivi.\n"
        "Usa un linguaggio professionale, senza slogan. Non inventare numeri: se non disponibili, indica range/ordini di grandezza.\n"
        "Cita le fonti in fondo come elenco sintetico (solo URL), senza quote testuali.\n"
    )
    user_prompt = (
        f"Titolo: {title}\n"
        f"Parole chiave: {', '.join(keywords or [])}\n"
        f"{srcs}\n"
        "Scrivi in italiano naturale. Evita frasi generiche; privilegia dettagli tecnici e punti pratici per l’acquisto."
    )

    try:
        resp = client.responses.create(
            model=model,
            input=[{"role":"system","content":sys_prompt},
                   {"role":"user","content":user_prompt}],
            temperature=0.6
        )
        body = getattr(resp, "output_text", "") or _template_body(title)
        schema = {
            "@context":"https://schema.org","@type":"FAQPage",
            "mainEntity":[
                {"@type":"Question","name":"Quali sono i punti di forza principali?","acceptedAnswer":{"@type":"Answer","text":"Vedi sezione 'Pro e contro' e 'Prova su strada'."}},
                {"@type":"Question","name":"Quanto costa gestirla in 5 anni?","acceptedAnswer":{"@type":"Answer","text":"Vedi 'Costi e alternative' e la tabella TCO."}},
                {"@type":"Question","name":"Quali ADAS sono inclusi?","acceptedAnswer":{"@type":"Answer","text":"Vedi sezione 'ADAS e infotainment'."}}
            ]
        }
        return body, schema
    except Exception as e:
        print("OpenAI fallback:", repr(e))
        return _template_body(title), None
