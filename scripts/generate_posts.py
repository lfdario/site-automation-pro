import argparse
from scripts.agents.ideation_auto import pick_topics
from scripts.agents.writer import generate_article
from scripts.agents.publisher import save_post

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=6)
    args = parser.parse_args()

    topics = pick_topics(args.count)
    for t in topics:
        title = t["title"]
        kws   = t.get("keywords", [])
        refs  = t.get("refs", [])
        body, schema = generate_article(title, kws, refs=refs)
        save_post(title, body, schema=schema, tags=kws, refs=refs)
        print(f"✔ Generated: {title}")

if __name__ == "__main__":
    main()
