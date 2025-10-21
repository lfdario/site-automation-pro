import pathlib, json, datetime
from slugify import slugify

ROOT = pathlib.Path(__file__).resolve().parents[2]

def _sanitize(obj):
    """Rende l'oggetto serializzabile in YAML/JSON (niente Ellipsis, Path, set, ecc.)."""
    import datetime as _dt
    from pathlib import Path

    if obj is Ellipsis:
        return None
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_sanitize(x) for x in obj]
    if isinstance(obj, set):
        return [_sanitize(x) for x in sorted(obj)]
    if isinstance(obj, dict):
        return {str(k): _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (Path, pathlib.PurePath)):
        return str(obj)
    if isinstance(obj, (_dt.date, _dt.datetime)):
        # ISO 8601
        return obj.isoformat()
    # fallback: stringa sicura
    try:
        return str(obj)
    except Exception:
        return None

def fm(**kwargs):
    import yaml as _y
    clean = _sanitize(kwargs)
    return "---\n" + _y.safe_dump(clean, sort_keys=False, allow_unicode=True) + "---\n\n"

def save_post(title, body, schema=None, tags=None):
    from datetime import datetime, timezone

    slug = slugify(str(title or "articolo"))
    dest = ROOT / 'content' / 'posts' / f'{slug}.md'
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Cover remota automatica (PaperMod legge anche params.images[0])
    cover_url = f"https://picsum.photos/seed/{slug}/1200/630"

    front = fm(
        title=str(title or "Articolo"),
        date=datetime.now(timezone.utc).isoformat(timespec='seconds'),
        draft=False,
        tags=_sanitize(tags) or [],
        categories=['Guide'],
        description=str(title or ""),
        images=[cover_url],
        cover=cover_url
    )

    content = front + f"![{title}]({cover_url})\n\n" + (body or "")
    if schema:
        try:
            content += "\n\n<script type=\"application/ld+json\">" + json.dumps(_sanitize(schema), ensure_ascii=False) + "</script>\n"
        except Exception:
            pass

    dest.write_text(content, encoding='utf-8')
    return dest
