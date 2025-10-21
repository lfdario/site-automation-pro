import os
import pathlib
import random
import requests

UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

def fetch_unsplash_image(query: str, out_dir: str = "static/images") -> str | None:
    """
    Cerca una foto su Unsplash e salva il file JPEG localmente.
    Ritorna il path relativo salvato (es. static/images/auto-123.jpg) oppure None.
    """
    if not UNSPLASH_KEY:
        print("⚠️  UNSPLASH_ACCESS_KEY mancante: salto download immagine.")
        return None

    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

    # 1) Cerca immagini
    r = requests.get(
        "https://api.unsplash.com/search/photos",
        headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
        params={"query": query, "orientation": "landscape", "per_page": 15},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    if not results:
        print(f"Nessun risultato Unsplash per query: {query}")
        return None

    photo = random.choice(results)
    img_url = photo["urls"]["regular"]
    img_id = photo["id"]

    # 2) Scarica immagine
    safe_query = "".join(c if c.isalnum() or c in "-_" else "-" for c in query.lower().replace(" ", "-"))
    img_path = pathlib.Path(out_dir) / f"{safe_query}-{img_id}.jpg"
    with requests.get(img_url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(img_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    # 3) Attribuzione suggerita da Unsplash
    author = photo["user"]["name"]
    author_url = photo["user"]["links"]["html"]
    print(f"Foto: {img_path} — di {author} ({author_url}) via Unsplash")

    return str(img_path).replace("\\", "/")
