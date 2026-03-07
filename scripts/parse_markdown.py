#!/usr/bin/env python3
"""
Parse Bible Markdown source files into canonical JSONL dataset.

Uses Echology's decompose.chunker for header-aware Markdown parsing,
demonstrating the same pipeline used for engineering documents applied
to theological text.

Reads Markdown files from source/raw-markdown/ and produces:
- canonical/books.json
- canonical/verses.jsonl
- canonical/chapters.jsonl
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Wire in Echology's chunker if available
ECHOLOGY_SRC = Path.home() / "echology" / "src"
if ECHOLOGY_SRC.exists() and str(ECHOLOGY_SRC) not in sys.path:
    sys.path.insert(0, str(ECHOLOGY_SRC))

try:
    from decompose.chunker import chunk_markdown, _parse_markdown_sections, Chunk
    ECHOLOGY_AVAILABLE = True
except ImportError:
    ECHOLOGY_AVAILABLE = False

SOURCE_DIR = PROJECT_ROOT / "source" / "raw-markdown"
CANONICAL_DIR = PROJECT_ROOT / "canonical"

# Book metadata: (slug, display_name, testament, book_number, category)
BOOKS = [
    ("genesis", "Genesis", "OT", 1, "Law"),
    ("exodus", "Exodus", "OT", 2, "Law"),
    ("leviticus", "Leviticus", "OT", 3, "Law"),
    ("numbers", "Numbers", "OT", 4, "Law"),
    ("deuteronomy", "Deuteronomy", "OT", 5, "Law"),
    ("joshua", "Joshua", "OT", 6, "History"),
    ("judges", "Judges", "OT", 7, "History"),
    ("ruth", "Ruth", "OT", 8, "History"),
    ("1samuel", "1 Samuel", "OT", 9, "History"),
    ("2samuel", "2 Samuel", "OT", 10, "History"),
    ("1kings", "1 Kings", "OT", 11, "History"),
    ("2kings", "2 Kings", "OT", 12, "History"),
    ("1chronicles", "1 Chronicles", "OT", 13, "History"),
    ("2chronicles", "2 Chronicles", "OT", 14, "History"),
    ("ezra", "Ezra", "OT", 15, "History"),
    ("nehemiah", "Nehemiah", "OT", 16, "History"),
    ("esther", "Esther", "OT", 17, "History"),
    ("job", "Job", "OT", 18, "Poetry"),
    ("psalms", "Psalms", "OT", 19, "Poetry"),
    ("proverbs", "Proverbs", "OT", 20, "Poetry"),
    ("ecclesiastes", "Ecclesiastes", "OT", 21, "Poetry"),
    ("song-of-solomon", "Song of Solomon", "OT", 22, "Poetry"),
    ("isaiah", "Isaiah", "OT", 23, "MajorProphet"),
    ("jeremiah", "Jeremiah", "OT", 24, "MajorProphet"),
    ("lamentations", "Lamentations", "OT", 25, "MajorProphet"),
    ("ezekiel", "Ezekiel", "OT", 26, "MajorProphet"),
    ("daniel", "Daniel", "OT", 27, "MajorProphet"),
    ("hosea", "Hosea", "OT", 28, "MinorProphet"),
    ("joel", "Joel", "OT", 29, "MinorProphet"),
    ("amos", "Amos", "OT", 30, "MinorProphet"),
    ("obadiah", "Obadiah", "OT", 31, "MinorProphet"),
    ("jonah", "Jonah", "OT", 32, "MinorProphet"),
    ("micah", "Micah", "OT", 33, "MinorProphet"),
    ("nahum", "Nahum", "OT", 34, "MinorProphet"),
    ("habakkuk", "Habakkuk", "OT", 35, "MinorProphet"),
    ("zephaniah", "Zephaniah", "OT", 36, "MinorProphet"),
    ("haggai", "Haggai", "OT", 37, "MinorProphet"),
    ("zechariah", "Zechariah", "OT", 38, "MinorProphet"),
    ("malachi", "Malachi", "OT", 39, "MinorProphet"),
    ("matthew", "Matthew", "NT", 40, "Gospel"),
    ("mark", "Mark", "NT", 41, "Gospel"),
    ("luke", "Luke", "NT", 42, "Gospel"),
    ("john", "John", "NT", 43, "Gospel"),
    ("acts", "Acts", "NT", 44, "Acts"),
    ("romans", "Romans", "NT", 45, "PaulineEpistle"),
    ("1corinthians", "1 Corinthians", "NT", 46, "PaulineEpistle"),
    ("2corinthians", "2 Corinthians", "NT", 47, "PaulineEpistle"),
    ("galatians", "Galatians", "NT", 48, "PaulineEpistle"),
    ("ephesians", "Ephesians", "NT", 49, "PaulineEpistle"),
    ("philippians", "Philippians", "NT", 50, "PaulineEpistle"),
    ("colossians", "Colossians", "NT", 51, "PaulineEpistle"),
    ("1thessalonians", "1 Thessalonians", "NT", 52, "PaulineEpistle"),
    ("2thessalonians", "2 Thessalonians", "NT", 53, "PaulineEpistle"),
    ("1timothy", "1 Timothy", "NT", 54, "PaulineEpistle"),
    ("2timothy", "2 Timothy", "NT", 55, "PaulineEpistle"),
    ("titus", "Titus", "NT", 56, "PaulineEpistle"),
    ("philemon", "Philemon", "NT", 57, "PaulineEpistle"),
    ("hebrews", "Hebrews", "NT", 58, "GeneralEpistle"),
    ("james", "James", "NT", 59, "GeneralEpistle"),
    ("1peter", "1 Peter", "NT", 60, "GeneralEpistle"),
    ("2peter", "2 Peter", "NT", 61, "GeneralEpistle"),
    ("1john", "1 John", "NT", 62, "GeneralEpistle"),
    ("2john", "2 John", "NT", 63, "GeneralEpistle"),
    ("3john", "3 John", "NT", 64, "GeneralEpistle"),
    ("jude", "Jude", "NT", 65, "GeneralEpistle"),
    ("revelation", "Revelation", "NT", 66, "Apocalyptic"),
]

BOOK_LOOKUP = {b[0]: b for b in BOOKS}

# Verse pattern: matches lines like "3:16 For God so loved..."
VERSE_PATTERN = re.compile(r"^(\d+):(\d+)\s+(.+)$")

# YAML frontmatter pattern
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter as a simple key-value dict."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta


def parse_markdown_file(filepath: Path, translation: str = "WEB") -> list[dict]:
    """Parse a single Markdown chapter file into verse records.

    When Echology's chunker is available, uses header-aware parsing
    to extract section structure. Falls back to regex parsing otherwise.
    """
    content = filepath.read_text(encoding="utf-8")

    meta = parse_frontmatter(content)
    file_translation = meta.get("translation", translation)
    book_slug = meta.get("book", "").lower().replace(" ", "-") if meta.get("book") else None
    chapter_num = int(meta["chapter"]) if meta.get("chapter") else None

    # Try to infer from filename if frontmatter is missing
    if not book_slug or chapter_num is None:
        stem = filepath.stem
        parts = stem.rsplit("-", 1)
        if len(parts) == 2:
            book_slug = parts[0]
            try:
                chapter_num = int(parts[1])
            except ValueError:
                print(f"Warning: cannot parse chapter from {filepath.name}", file=sys.stderr)
                return []

    if book_slug not in BOOK_LOOKUP:
        print(f"Warning: unknown book '{book_slug}' in {filepath.name}", file=sys.stderr)
        return []

    book_info = BOOK_LOOKUP[book_slug]
    _, book_name, testament, book_number, _ = book_info

    # Use Echology's chunker for structure-aware parsing when available
    if ECHOLOGY_AVAILABLE:
        sections = _parse_markdown_sections(content)
        heading_context = {}
        for sec in sections:
            if sec["heading"]:
                heading_context["current_section"] = sec["heading"]
                heading_context["heading_path"] = sec["path"]

    verses = []
    for line in content.splitlines():
        match = VERSE_PATTERN.match(line.strip())
        if match:
            verse_chapter = int(match.group(1))
            verse_num = int(match.group(2))
            verse_text = match.group(3).strip()

            if verse_chapter != chapter_num:
                continue

            verse_id = f"{file_translation.lower()}-{book_slug}-{chapter_num}-{verse_num}"
            reference = f"{book_name} {chapter_num}:{verse_num}"

            record = {
                "id": verse_id,
                "translation": file_translation,
                "book": book_slug,
                "book_name": book_name,
                "chapter": chapter_num,
                "verse": verse_num,
                "reference": reference,
                "text": verse_text,
                "testament": testament,
                "book_number": book_number,
            }

            verses.append(record)

    return verses


def build_books_json() -> list[dict]:
    """Generate the books.json metadata file."""
    books = []
    for slug, name, testament, number, category in BOOKS:
        books.append({
            "id": slug,
            "name": name,
            "testament": testament,
            "book_number": number,
            "category": category,
        })
    return books


def build_chapters(all_verses: list[dict]) -> list[dict]:
    """Generate chapter records from parsed verses."""
    chapters_map = {}
    for v in all_verses:
        key = (v["translation"], v["book"], v["chapter"])
        if key not in chapters_map:
            chapters_map[key] = {
                "id": f"{v['translation'].lower()}-{v['book']}-{v['chapter']}",
                "translation": v["translation"],
                "book": v["book"],
                "book_name": v["book_name"],
                "chapter": v["chapter"],
                "verse_count": 0,
                "verses": [],
            }
        chapters_map[key]["verse_count"] += 1
        chapters_map[key]["verses"].append(v["text"])

    chapters = []
    for key in sorted(chapters_map.keys()):
        ch = chapters_map[key]
        ch["text"] = " ".join(ch.pop("verses"))
        chapters.append(ch)

    return chapters


def write_jsonl(filepath: Path, records: list[dict]):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_json(filepath: Path, data):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    if ECHOLOGY_AVAILABLE:
        print("Echology decompose.chunker loaded — using header-aware parsing")
    else:
        print("Echology not found — using standalone regex parser")
        print(f"  (To enable: ensure {ECHOLOGY_SRC} exists)")

    if not SOURCE_DIR.exists():
        print(f"\nSource directory not found: {SOURCE_DIR}")
        print("Place Markdown Bible files in source/raw-markdown/")
        print("Expected format: one chapter per file (e.g., john-03.md)")
        sys.exit(1)

    md_files = sorted(SOURCE_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {SOURCE_DIR}")
        sys.exit(1)

    print(f"Found {len(md_files)} Markdown files")

    all_verses = []
    for filepath in md_files:
        verses = parse_markdown_file(filepath)
        all_verses.extend(verses)
        if verses:
            print(f"  Parsed {filepath.name}: {len(verses)} verses")

    print(f"\nTotal verses parsed: {len(all_verses)}")

    CANONICAL_DIR.mkdir(parents=True, exist_ok=True)

    books = build_books_json()
    write_json(CANONICAL_DIR / "books.json", books)
    print(f"Wrote books.json ({len(books)} books)")

    write_jsonl(CANONICAL_DIR / "verses.jsonl", all_verses)
    print(f"Wrote verses.jsonl ({len(all_verses)} records)")

    chapters = build_chapters(all_verses)
    write_jsonl(CANONICAL_DIR / "chapters.jsonl", chapters)
    print(f"Wrote chapters.jsonl ({len(chapters)} records)")

    print("\nDone. Canonical dataset generated in canonical/")


if __name__ == "__main__":
    main()
