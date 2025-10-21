import pathlib, json, datetime
from slugify import slugify

ROOT = pathlib.Path(__file__).resolve().parents[2]

def fm(**kwargs):
    import yaml as _y
    return "---\n" + _y.safe_dump(kwargs, sort_keys=False, allow_unicode=True) + "---\n\n"

def save_post(title, body, schema=None, tags=None):
    slug = slugify(title)
    dest = ROOT / 'content' / 'posts' / f'{slug}.md'
    dest.parent.mkdir(parents=True, exist_ok=True)

    cover_url = f"https://picsum.photos/seed/{slug}/1200/630"

    front = fm(
    title=title,
    date=...,
    draft=False,
    tags=tags or [],
    categories=['Guide'],
    description=title,
    images=[cover_url],     # PaperMod usa questo per og:image e cover
    cover=cover_url
)

    content = front + f"![{title}]({cover_url})\n\n" + body
    if schema:
        content += "\n\n<script type=\"application/ld+json\">" + json.dumps(schema, ensure_ascii=False) + "</script>\n"

    dest.write_text(content, encoding='utf-8')
    return dest
