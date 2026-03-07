#!/usr/bin/env python3
"""
Build the Scripture cross-reference graph.

Reads canonical verse data and cross-reference sources to produce:
- graph/nodes.jsonl
- graph/edges.jsonl

Cross-reference sources:
- Open Bible cross-references (TSV format, "Gen.1.1" style refs)
- Custom additions in graph/custom_edges.jsonl
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CANONICAL_DIR = PROJECT_ROOT / "canonical"
GRAPH_DIR = PROJECT_ROOT / "graph"

# Map Open Bible abbreviated book names (dot-separated) to OSI slugs
OPENBIBLE_BOOK_MAP = {
    "Gen": "genesis", "Exod": "exodus", "Lev": "leviticus", "Num": "numbers",
    "Deut": "deuteronomy", "Josh": "joshua", "Judg": "judges", "Ruth": "ruth",
    "1Sam": "1samuel", "2Sam": "2samuel", "1Kgs": "1kings", "2Kgs": "2kings",
    "1Chr": "1chronicles", "2Chr": "2chronicles", "Ezra": "ezra",
    "Neh": "nehemiah", "Esth": "esther", "Job": "job", "Ps": "psalms",
    "Prov": "proverbs", "Eccl": "ecclesiastes", "Song": "song-of-solomon",
    "Isa": "isaiah", "Jer": "jeremiah", "Lam": "lamentations", "Ezek": "ezekiel",
    "Dan": "daniel", "Hos": "hosea", "Joel": "joel", "Amos": "amos",
    "Obad": "obadiah", "Jonah": "jonah", "Mic": "micah", "Nah": "nahum",
    "Hab": "habakkuk", "Zeph": "zephaniah", "Hag": "haggai", "Zech": "zechariah",
    "Mal": "malachi", "Matt": "matthew", "Mark": "mark", "Luke": "luke",
    "John": "john", "Acts": "acts", "Rom": "romans", "1Cor": "1corinthians",
    "2Cor": "2corinthians", "Gal": "galatians", "Eph": "ephesians",
    "Phil": "philippians", "Col": "colossians", "1Thess": "1thessalonians",
    "2Thess": "2thessalonians", "1Tim": "1timothy", "2Tim": "2timothy",
    "Titus": "titus", "Phlm": "philemon", "Heb": "hebrews",
    "Jas": "james", "1Pet": "1peter", "2Pet": "2peter",
    "1John": "1john", "2John": "2john", "3John": "3john",
    "Jude": "jude", "Rev": "revelation",
}

# Pattern for Open Bible refs: "Gen.1.1" or "Ps.89.11-Ps.89.12"
OPENBIBLE_REF = re.compile(r"^([A-Za-z0-9]+)\.(\d+)\.(\d+)$")


def parse_openbible_ref(ref_str: str, translation: str = "kjv") -> str | None:
    """Convert 'Gen.1.1' to 'kjv-genesis-1-1'."""
    match = OPENBIBLE_REF.match(ref_str.strip())
    if not match:
        return None
    book_abbrev = match.group(1)
    chapter = int(match.group(2))
    verse = int(match.group(3))
    slug = OPENBIBLE_BOOK_MAP.get(book_abbrev)
    if not slug:
        return None
    return f"{translation}-{slug}-{chapter}-{verse}"


def build_nodes_from_verses() -> list[dict]:
    """Create graph nodes from canonical verses."""
    verses_file = CANONICAL_DIR / "verses.jsonl"
    if not verses_file.exists():
        print(f"Error: {verses_file} not found. Run parse_markdown.py first.")
        sys.exit(1)

    nodes = []
    with open(verses_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                v = json.loads(line)
                nodes.append({
                    "id": v["id"],
                    "type": "verse",
                    "reference": v["reference"],
                    "book": v["book"],
                    "chapter": v["chapter"],
                    "verse": v["verse"],
                    "testament": v["testament"],
                })
    return nodes


def load_openbible_crossrefs(filepath: Path, translation: str = "kjv") -> list[dict]:
    """
    Load cross-references from Open Bible TSV format.

    Format: "From Verse\tTo Verse\tVotes"
    Example: "Gen.1.1\tPs.96.5\t58"

    Range refs like "Ps.89.11-Ps.89.12" are resolved to the first verse.
    """
    if not filepath.exists():
        return []

    edges = []
    skipped = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("From") or line.startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) < 3:
                skipped += 1
                continue

            from_raw = parts[0].strip()
            to_raw = parts[1].strip()
            try:
                votes = int(parts[2].strip())
            except ValueError:
                votes = 0

            # Handle range refs: take first verse of range
            from_ref = from_raw.split("-")[0]
            to_ref = to_raw.split("-")[0]

            from_id = parse_openbible_ref(from_ref, translation)
            to_id = parse_openbible_ref(to_ref, translation)

            if from_id and to_id:
                edges.append({
                    "from": from_id,
                    "to": to_id,
                    "type": "cross_reference",
                    "confidence": min(votes / 100.0, 1.0),
                    "votes": votes,
                    "source": "openbible_crossrefs",
                })
            else:
                skipped += 1

    if skipped:
        print(f"  Skipped {skipped} unparseable refs")

    return edges


def write_jsonl(filepath: Path, records: list[dict]):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)

    print("Building graph nodes from canonical verses...")
    nodes = build_nodes_from_verses()
    write_jsonl(GRAPH_DIR / "nodes.jsonl", nodes)
    print(f"  Wrote {len(nodes)} nodes")

    print("\nLoading cross-reference data...")

    edges = []

    # Try TSV format first (Open Bible download)
    tsv_file = GRAPH_DIR / "cross_references.txt"
    if tsv_file.exists():
        print(f"  Reading {tsv_file.name}...")
        edges = load_openbible_crossrefs(tsv_file)
    else:
        # Try CSV format
        csv_file = GRAPH_DIR / "cross_references.csv"
        if csv_file.exists():
            print(f"  Reading {csv_file.name}...")
            edges = load_openbible_crossrefs(csv_file)

    # Load custom edges if they exist
    custom_file = GRAPH_DIR / "custom_edges.jsonl"
    if custom_file.exists():
        print("  Loading custom edges...")
        with open(custom_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    edges.append(json.loads(line))

    if edges:
        write_jsonl(GRAPH_DIR / "edges.jsonl", edges)
        print(f"  Wrote {len(edges)} edges")
    else:
        print("  No cross-reference data found.")
        print(f"  To add cross-references:")
        print(f"    1. Download from https://www.openbible.info/labs/cross-references/")
        print(f"    2. Unzip and place cross_references.txt in graph/")
        print(f"    3. Re-run this script")
        write_jsonl(GRAPH_DIR / "edges.jsonl", [])

    print(f"\nDone. Graph generated in graph/")


if __name__ == "__main__":
    main()
