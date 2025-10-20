
import os, random, json
from openai import OpenAI

def generate_article(title, keywords, model='gpt-4o-mini', min_words=900, max_words=1400, tone='chiaro e pratico'):
    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    target_len = random.randint(min_words, max_words)
    if not api_key:
        return f"""## Introduzione
In questa guida spieghiamo **{title.lower()}** con istruzioni passo-passo.

## Passaggi rapidi
1. Passo 1
2. Passo 2
3. Passo 3

## FAQ
**Domanda:** Quanto è difficile?  
**Risposta:** Segui i passaggi indicati.

""", None
    client = OpenAI(api_key=api_key)
    sys_prompt = f"""Sei un redattore tecnico italiano. Stile {tone}.
Lunghezza {min_words}-{max_words} parole. Includi H2/H3, esempi e 3-5 FAQ concise."""
    user_prompt = f"""Titolo: {title}
Parole chiave: {', '.join(keywords)}
Scrivi un articolo completo in italiano, pratico, con passi numerati e checklist finale."""
    resp = client.responses.create(model=model, input=[
        {"role":"system","content":sys_prompt},
        {"role":"user","content":user_prompt}
    ], temperature=0.7)
    try:
        body = resp.output_text
    except Exception:
        body = "## Introduzione\nArticolo in aggiornamento.\n"
    schema = {
        "@context":"https://schema.org","@type":"FAQPage",
        "mainEntity":[
            {"@type":"Question","name":"Quali sono i passaggi principali?","acceptedAnswer":{"@type":"Answer","text":"Segui i passaggi descritti."}}
        ]
    }
    return body, schema
