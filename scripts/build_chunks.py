#!/usr/bin/env python3
"""
Build chunk layers from canonical verse data.

Reads canonical/verses.jsonl and produces:
- chunks/by_verse/*.jsonl
- chunks/by_chapter/*.jsonl
- chunks/by_passage/*.jsonl (sliding window passages)
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CANONICAL_DIR = PROJECT_ROOT / "canonical"
CHUNKS_DIR = PROJECT_ROOT / "chunks"

# Default passage window size
PASSAGE_SIZE = 5  # verses per passage
PASSAGE_STRIDE = 3  # slide by 3 for overlap


def load_verses() -> list[dict]:
    """Load all verses from canonical JSONL."""
    verses_file = CANONICAL_DIR / "verses.jsonl"
    if not verses_file.exists():
        print(f"Error: {verses_file} not found. Run parse_markdown.py first.")
        sys.exit(1)

    verses = []
    with open(verses_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                verses.append(json.loads(line))
    return verses


def build_verse_chunks(verses: list[dict]) -> list[dict]:
    """Each verse becomes its own chunk."""
    chunks = []
    for v in verses:
        chunks.append({
            "id": v["id"],
            "type": "verse",
            "translation": v["translation"],
            "book": v["book"],
            "chapter": v["chapter"],
            "verse": v["verse"],
            "reference": v["reference"],
            "text": v["text"],
        })
    return chunks


def build_chapter_chunks(verses: list[dict]) -> list[dict]:
    """Group verses by chapter into chapter-level chunks."""
    chapters = defaultdict(list)
    for v in verses:
        key = (v["translation"], v["book"], v["chapter"])
        chapters[key].append(v)

    chunks = []
    for key in sorted(chapters.keys()):
        ch_verses = chapters[key]
        first = ch_verses[0]
        last = ch_verses[-1]
        chunks.append({
            "id": f"{first['translation'].lower()}-{first['book']}-{first['chapter']}",
            "type": "chapter",
            "translation": first["translation"],
            "book": first["book"],
            "book_name": first["book_name"],
            "chapter": first["chapter"],
            "start_reference": first["reference"],
            "end_reference": last["reference"],
            "verse_ids": [v["id"] for v in ch_verses],
            "verse_count": len(ch_verses),
            "text": " ".join(v["text"] for v in ch_verses),
        })
    return chunks


def build_passage_chunks(verses: list[dict], window: int = PASSAGE_SIZE, stride: int = PASSAGE_STRIDE) -> list[dict]:
    """Create overlapping passage chunks using a sliding window within each chapter."""
    chapters = defaultdict(list)
    for v in verses:
        key = (v["translation"], v["book"], v["chapter"])
        chapters[key].append(v)

    chunks = []
    for key in sorted(chapters.keys()):
        ch_verses = chapters[key]
        if len(ch_verses) <= window:
            # Whole chapter is one passage
            first = ch_verses[0]
            last = ch_verses[-1]
            chunks.append({
                "id": f"{first['translation'].lower()}-{first['book']}-{first['chapter']}-{first['verse']}-{last['verse']}",
                "type": "passage",
                "translation": first["translation"],
                "book": first["book"],
                "book_name": first["book_name"],
                "chapter": first["chapter"],
                "start_verse": first["verse"],
                "end_verse": last["verse"],
                "start_reference": first["reference"],
                "end_reference": last["reference"],
                "verse_ids": [v["id"] for v in ch_verses],
                "text": " ".join(v["text"] for v in ch_verses),
            })
        else:
            for i in range(0, len(ch_verses) - window + 1, stride):
                segment = ch_verses[i:i + window]
                first = segment[0]
                last = segment[-1]
                chunks.append({
                    "id": f"{first['translation'].lower()}-{first['book']}-{first['chapter']}-{first['verse']}-{last['verse']}",
                    "type": "passage",
                    "translation": first["translation"],
                    "book": first["book"],
                    "book_name": first["book_name"],
                    "chapter": first["chapter"],
                    "start_verse": first["verse"],
                    "end_verse": last["verse"],
                    "start_reference": first["reference"],
                    "end_reference": last["reference"],
                    "verse_ids": [v["id"] for v in segment],
                    "text": " ".join(v["text"] for v in segment),
                })
            # Ensure last verses are covered
            if (len(ch_verses) - window) % stride != 0:
                segment = ch_verses[-window:]
                first = segment[0]
                last = segment[-1]
                chunk_id = f"{first['translation'].lower()}-{first['book']}-{first['chapter']}-{first['verse']}-{last['verse']}"
                if not any(c["id"] == chunk_id for c in chunks):
                    chunks.append({
                        "id": chunk_id,
                        "type": "passage",
                        "translation": first["translation"],
                        "book": first["book"],
                        "book_name": first["book_name"],
                        "chapter": first["chapter"],
                        "start_verse": first["verse"],
                        "end_verse": last["verse"],
                        "start_reference": first["reference"],
                        "end_reference": last["reference"],
                        "verse_ids": [v["id"] for v in segment],
                        "text": " ".join(v["text"] for v in segment),
                    })
    return chunks


def write_jsonl(filepath: Path, records: list[dict]):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    print("Loading canonical verses...")
    verses = load_verses()
    print(f"Loaded {len(verses)} verses")

    print("\nBuilding verse chunks...")
    verse_chunks = build_verse_chunks(verses)
    write_jsonl(CHUNKS_DIR / "by_verse" / "verse_chunks.jsonl", verse_chunks)
    print(f"  Wrote {len(verse_chunks)} verse chunks")

    print("Building chapter chunks...")
    chapter_chunks = build_chapter_chunks(verses)
    write_jsonl(CHUNKS_DIR / "by_chapter" / "chapter_chunks.jsonl", chapter_chunks)
    print(f"  Wrote {len(chapter_chunks)} chapter chunks")

    print("Building passage chunks...")
    passage_chunks = build_passage_chunks(verses)
    write_jsonl(CHUNKS_DIR / "by_passage" / "passage_chunks.jsonl", passage_chunks)
    print(f"  Wrote {len(passage_chunks)} passage chunks")

    print(f"\nDone. Chunks generated in chunks/")


if __name__ == "__main__":
    main()
