import feedparser, random, re, time

FEEDS = [
    "https://www.autoblog.com/rss.xml",
    "https://www.topgear.com/it/latest/rss",           # se non valido, verrà ignorato
    "https://www.motor1.com/rss/news/",
    "https://www.quattroruote.it/rss/homepage.xml",    # può limitare full text ma basta per titoli
    "https://www.formulapassion.it/feed",              # motorsport/tech
]

def _clean(t):
    t = re.sub(r"<[^>]+>", "", str(t or ""))
    t = re.sub(r"\s+", " ", t).strip()
    return t

def fetch_candidates(max_per_feed=8):
    items = []
    for url in FEEDS:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:max_per_feed]:
                title = _clean(getattr(e, "title", ""))
                if not title: continue
                summ  = _clean(getattr(e, "summary", ""))
                link  = getattr(e, "link", "")
                items.append({"title": title, "summary": summ, "source": link})
        except Exception:
            continue
        time.sleep(0.2)
    return items

def pick_topics(n=6):
    pool = fetch_candidates()
    random.shuffle(pool)
    topics = []
    used = set()
    for it in pool:
        t = it["title"]
        # Regole semplici: escludi promo/rumor poveri
        if any(bad in t.lower() for bad in ["sconto", "offerta", "advertorial"]): 
            continue
        key = re.sub(r"[^a-z0-9]+","-",t.lower())
        if key in used: 
            continue
        used.add(key)
        # tag/keywords di base
        kws = []
        for k in ["elettrico","plug-in","mild hybrid","autonomia","ricarica","consumi","cavalli",
                  "costo","allestimenti","ADAS","infotainment","motore","batteria","garanzia"]:
            if k in (it["summary"]+" "+t).lower(): kws.append(k)
        topics.append({
            "title": t,
            "keywords": kws[:6],
            "refs": [it["source"]] if it["source"] else []
        })
        if len(topics) >= n: break
    # se feed poveri, fallback su macro-temi
    if not topics:
        topics = [
            {"title":"Auto elettriche 2025: autonomie reali e ricarica veloce a confronto", "keywords":["elettrico","autonomia","ricarica","consumi"], "refs":[]},
            {"title":"ADAS 2025: quali assistenti sono davvero utili su strada?", "keywords":["ADAS","sicurezza","cruise adattivo"], "refs":[]},
        ]
    return topics
