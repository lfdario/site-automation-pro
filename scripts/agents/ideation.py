
import random, pathlib, yaml
ROOT = pathlib.Path(__file__).resolve().parents[2]

def pick_topics(n=2):
    topics = [t.strip() for t in open(ROOT/'topics'/'topics.txt', encoding='utf-8').read().splitlines() if t.strip()]
    random.shuffle(topics)
    return topics[:n]
