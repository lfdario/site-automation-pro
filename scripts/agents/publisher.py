import os
import pathlib, json
from datetime import datetime, timezone
from slugify import slugify

import requests

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATIC_IMG_DIR = ROOT / "static" / "images"
STATIC_IMG_DIR.mkdir(parents=True, exist_ok=True)

UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "").strip()

def _sanitize(obj):
    import datetime as _dt
    from pathlib import Path
    if obj is Ellipsis:
        return None
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_sanitize(x) for x in obj]
    if isinstance(obj, set):
        return sorted([_sanitize(x) for x in obj])
    if isinstance(obj, dict):
        return {str(k): _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (Path, pathlib.PurePath)):
        return str(obj)
    if isinstance(obj, (_dt.date, _dt.datetime)):
        return obj.isoformat()
    try:
        return str(obj)
    except Exception:
        return None

def fm(**kwargs):
    import yaml as _y
    clean = _sanitize(kwargs)
    return "---\n" + _y.safe_dump(clean, sort_keys=False, allow_unicode=True) + "---\n\n"

def _unsplash_search(query: str):
    """Ritorna (url_download, credit_str) oppure (None, None) se fallisce."""
    if not UNSPLASH_KEY:
        return None, None
    try:
        # Cerca foto orizzontali “pulite”
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": 1, "orientation": "landscape", "content_filter": "high"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("results"):
            return None, None
        res = data["results"][0]
        # url "regular" va benissimo per cover (1200x630 circa)
        url = res["urls"].get("regular") or res["urls"].get("full")
        user = res.get("user", {})
        name = user.get("name") or user.get("username") or "Unsplash"
        link = user.get("links", {}).get("html") or "https://unsplash.com"
        credit = f"Foto: {name} via Unsplash"
        # Nota: per maggior aderenza alle linee guida Unsplash, potresti aggiungere un link di attribuzione nella pagina (già gestito sotto).
        return url, credit
    except Exception:
        return None, None

def _download_to_static(url: str, dest_path: pathlib.Path) -> bool:
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception:
        return False

def _get_thematic_image(slug: str, title: str, tags):
    """Cerca un'immagine coerente (Unsplash). Ritorna (front_url, credit_text)."""
    query_terms = [title] + (tags or [])
    # forza contesto automotive
    query = ", ".join([t for t in query_terms if t]) + ", car, automotive"
    # prova Unsplash
    url, credit = _unsplash_search(query)
    if url:
        dest = STATIC_IMG_DIR / f"{slug}.jpg"
        if _download_to_static(url, dest):
            # IMPORTANTE: per GitHub Pages "project pages" evita slash iniziale
            front_url = f"images/{slug}.jpg"
            return front_url, credit
    # fallback: picsum (nessun download, URL remoto)
    fallback = f"https://picsum.photos/seed/{slug}/1200/630"
    return fallback, None

def save_post(title, body, schema=None, tags=None, refs=None):
    slug = slugify(str(title or "articolo"))
    dest = ROOT / "content" / "posts" / f"{slug}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)

    cover_url, credit = _get_thematic_image(slug, str(title or ""), tags)

    front = fm(
        title=str(title or "Articolo"),
        date=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        draft=False,
        tags=_sanitize(tags) or ["auto"],
        categories=["Auto", "Guide"],
        description=str(title or ""),
        images=[cover_url],   # PaperMod usa questo per og:image e cover
        cover=cover_url,
        sources=_sanitize(refs) or [],
    )

    # hero + contenuto
    content = front + f"![{title}]({cover_url})\n\n" + (body or "")
    if refs:
        content += "\n\n## Fonti\n" + "\n".join(f"- {u}" for u in refs)
    if credit:
        content += f"\n\n<div style=\"font-size:0.9em;opacity:.75\">{credit}</div>"

    if schema:
        try:
            content += "\n\n<script type=\"application/ld+json\">" + json.dumps(_sanitize(schema), ensure_ascii=False) + "</script>\n"
        except Exception:
            pass

    dest.write_text(content, encoding="utf-8")
    return dest
