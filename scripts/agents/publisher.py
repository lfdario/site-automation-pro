
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
    front = fm(
        title=title,
        date=datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        draft=False,
        tags=tags or [],
        categories=['Guide'],
        description=title,
        cover=f"/images/{slug}.svg"
    )
    # minimalist SVG cover
    img = (ROOT/'static'/'images'/f'{slug}.svg')
    img.parent.mkdir(parents=True, exist_ok=True)
    img.write_text(f"""<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='630'>
<rect width='100%' height='100%' fill='#f2f2f2'/>
<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='48' fill='#333'>{title}</text>
</svg>""", encoding='utf-8')
    content = front + f"![{title}](/images/{slug}.svg)\n\n" + body
    if schema:
        content += "\n\n<script type=\"application/ld+json\">" + json.dumps(schema, ensure_ascii=False) + "</script>\n"
    dest.write_text(content, encoding='utf-8')
    return dest
