import argparse
import datetime
import os
import pathlib
import random
import sys
from textwrap import dedent

from openai import OpenAI
from scripts.unsplash_helper import fetch_unsplash_image

# Argomenti a tema automotive
CATEGORIES = [
    ("news",      ["novità modelli", "saloni auto", "tecnologia", "ADAS", "motorsport"]),
    ("prove",     ["prova su strada", "test drive", "handling", "consumi reali", "interni"]),
    ("elettrico", ["auto elettriche", "ricarica rapida", "batterie", "autonomia", "wallbox"]),
    ("guide",     ["assicurazione auto", "manutenzione", "pneumatici", "bollo", "revisioni"]),
    ("mercato",   ["incentivi auto", "prezzi e listini", "promozioni", "noleggio", "leasing"]),
]

TOPICS = [
    "le 10 auto elettriche da comprare nel 2025",
    "SUV compatti: confronto modelli 2025",
    "ricarica rapida: verità su tempi e degrado batteria",
    "prova su strada: citycar ibrida nei tragitti urbani",
    "ADAS: quali sistemi valgono davvero",
    "incentivi auto: come massimizzare lo sconto",
    "manutenzione EV: costi nascosti e miti da sfatare",
    "pneumatici: estivi vs quattro stagioni",
    "connettività in auto: Android Auto, CarPlay e app",
    "leasing vs acquisto: cosa conviene nel 2025",
]

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def pick_topic_and_category():
    category, _ = random.choice(CATEGORIES)
    topic = random.choice(TOPICS)
    return topic, category

def to_slug(s: str) -> str:
    s = s.strip().lower().replace(" ", "-")
    return "".join(c for c in s if c.isalnum() or c in "-_")

def already_exists(out_dir: pathlib.Path, slug: str) -> bool:
    return (out_dir / f"{slug}.md").exists()

def build_prompt(topic: str, category: str) -> str:
    return dedent(f"""
    Scrivi un articolo approfondito, in italiano, sul tema "{topic}" (categoria: {category}).
    Requisiti:
    - 900–1200 parole, tono giornalistico, chiaro e professionale.
    - Struttura con H2/H3, paragrafi brevi, elenchi puntati dove utile.
    - Box iniziale "In breve" con 3–5 bullet sintetici.
    - Conclusione con takeaway pratici.
    - Inserisci parole chiave SEO pertinenti.
    - Evita ripetizioni e contenuti generici.
    - Non usare markup HTML, solo Markdown.
    """)

def generate_article(client: OpenAI, topic: str, category: str) -> str:
    prompt = build_prompt(topic, category)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()

def write_post(topic: str, category: str, body: str, image_path: str | None, out_dir: pathlib.Path) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = to_slug(topic)
    date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    rel_img = image_path.replace("static/", "/") if image_path else ""

    # Mettiamo featured su alcune categorie per popolare la hero
    featured = "true" if category in ("news", "elettrico") else "false"

    front = f"""---
title: "{topic.title()}"
date: {date}
draft: false
categories: ["{category}"]
tags: ["auto","{category}"]
image: "{rel_img}"
description: "Approfondimento su {topic}."
featured: {featured}
---
"""

    fp = out_dir / f"{slug}.md"
    fp.write_text(front + "\n" + body + "\n", encoding="utf-8")
    return fp

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3, help="Numero di articoli da generare")
    args = parser.parse_args()

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        print("❌ OPENAI_API_KEY mancante.")
        sys.exit(1)

    client = OpenAI(api_key=openai_key)
    posts_dir = pathlib.Path("content/posts")
    generated = 0
    attempts = 0
    max_attempts = args.count * 3  # evita loop infinito in caso di duplicati

    while generated < args.count and attempts < max_attempts:
        attempts += 1
        topic, category = pick_topic_and_category()
        slug = to_slug(topic)
        if already_exists(posts_dir, slug):
            print(f"↩️  Esiste già: {slug}, scelgo un altro topic.")
            continue

        print(f"🧠 Genero: {topic} [{category}]")
        body = generate_article(client, topic, category)

        print(f"📸 Immagine per '{topic}'...")
        img = fetch_unsplash_image(query=topic)

        fp = write_post(topic, category, body, img, posts_dir)
        print(f"✅ Post creato: {fp}")
        if img:
            print(f"🖼️  Immagine: {img.replace('static/', '/')}")
        generated += 1

    if generated < args.count:
        print(f"⚠️ Generati {generated}/{args.count} post (limite tentativi)")

if __name__ == "__main__":
    main()
