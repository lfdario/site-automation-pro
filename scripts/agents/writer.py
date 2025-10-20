import os, random
from openai import OpenAI

def _template_body(title):
    return f"""## Introduzione
In questa guida spieghiamo **{title}** con istruzioni passo-passo.

## Passaggi rapidi
1. Passo 1
2. Passo 2
3. Passo 3

## Consigli pratici
- Suggerimento A
- Suggerimento B
- Suggerimento C

## FAQ
**Domanda:** Come procedo se qualcosa non funziona?  
**Risposta:** Ripeti i passaggi e verifica le note nella guida.

"""

def generate_article(title, keywords, model='gpt-4o-mini', min_words=900, max_words=1400, tone='chiaro e pratico'):
    api_key = os.environ.get('OPENAI_API_KEY','').strip()

    # Fallback immediato se non c'è la chiave
    if not api_key:
        return _template_body(title), None

    try:
        client = OpenAI(api_key=api_key)
        sys_prompt = f"Sei un redattore tecnico italiano. Stile {tone}. Lunghezza {min_words}-{max_words} parole. Includi H2/H3, esempi e 3-5 FAQ concise."
        user_prompt = f"Titolo: {title}\nParole chiave: {', '.join(keywords)}\nScrivi un articolo completo in italiano, pratico, con passi numerati e checklist finale."
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
                {"@type":"Question","name":"Quali sono i passaggi principali?","acceptedAnswer":{"@type":"Answer","text":"Segui i passaggi descritti."}}
            ]
        }
        return body, schema

    except Exception as e:
        # Qualsiasi errore (429 quota, rete, ecc.) => fallback
        print("OpenAI fallback:", repr(e))
        return _template_body(title), None
