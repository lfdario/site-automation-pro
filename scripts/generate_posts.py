# scripts/generate_posts.py
import os
import random
import datetime
import pathlib
from openai import OpenAI
from scripts.unsplash_helper import fetch_unsplash_image

# Argomenti esempio
TOPICS = [
    "auto elettriche",
    "SUV 2025",
    "tecnologia automobilistica",
    "motori ibridi",
    "novità automotive",
    "ricarica rapida EV",
]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post(topic: str, output_dir="content/posts"):
    """Genera un post markdown con titolo, testo e immagine Unsplash."""
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Genera titolo + testo con OpenAI
    prompt = f"""
    Scrivi un articolo approfondito e professionale sul tema "{topic}".
    Il tono deve essere giornalistico, chiaro e informativo, con almeno 500 parole.
    Includi un'introduzione, 2-3 sezioni e una conclusione.
    """
    print(f"🧠 Genero articolo su: {topic}")
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    text = completion.choices[0].message.content.strip()

    # Scarica immagine coerente
    print(f"📸 Scarico immagine da Unsplash per '{topic}'...")
    image_path = fetch_unsplash_image(query=topic)
    rel_image_path = image_path.replace("static/", "/") if image_path else ""

    # Prepara front matter per Hugo
    title = topic.title()
    date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    filename = pathlib.Path(output_dir) / f"{topic.replace(' ', '-')}.md"

    front_matter = f"""---
title: "{title}"
date: {date}
draft: false
tags: ["auto", "news"]
image: "{rel_image_path}"
description: "Articolo su {topic} con approfondimenti e tendenze."
---
"""

    # Scrivi file Markdown
    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + "\n" + text + "\n")

    print(f"✅ Post generato: {filename}")
    if image_path:
        print(f"🖼️  Immagine: {rel_image_path}")

def main(count=3):
    """Genera N post casuali"""
    for i in range(count):
        topic = random.choice(TOPICS)
        generate_post(topic)

if __name__ == "__main__":
    main()
