import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse, pathlib, yaml, random
from scripts.agents.ideation import pick_topics
from scripts.agents.writer import generate_article
from scripts.agents.editor import optimize
from scripts.agents.publisher import save_post

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load(open(ROOT / "config" / "site.yaml", "r", encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=2)
    args = ap.parse_args()

    topics = pick_topics(args.count)
    for t in topics:
        title = t[:1].upper() + t[1:]
        kws = [w for w in t.split() if len(w) > 3][:3]
        body, schema = generate_article(title, kws, model=CONFIG["model"],
                                        min_words=CONFIG["min_words"], max_words=CONFIG["max_words"],
                                        tone=CONFIG["tone"])
        body = optimize(body)
        save_post(title, body, schema=schema, tags=kws)

if __name__ == "__main__":
    main()
