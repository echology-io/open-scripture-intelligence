#!/usr/bin/env python3
"""
Import KJV Bible from thiagobodruk/bible JSON format into OSI Markdown source.

Source: https://github.com/thiagobodruk/bible (MIT License)
Translation: KJV (King James Version) — Public Domain

Converts JSON array of books -> one Markdown file per chapter in source/raw-markdown/
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "source" / "raw-markdown"

# Map JSON abbreviations to OSI book slugs
ABBREV_TO_SLUG = {
    "gn": "genesis", "ex": "exodus", "lv": "leviticus", "nm": "numbers",
    "dt": "deuteronomy", "js": "joshua", "jud": "judges", "rt": "ruth",
    "1sm": "1samuel", "2sm": "2samuel", "1kgs": "1kings", "2kgs": "2kings",
    "1ch": "1chronicles", "2ch": "2chronicles", "ezr": "ezra",
    "ne": "nehemiah", "et": "esther", "job": "job", "ps": "psalms",
    "prv": "proverbs", "ec": "ecclesiastes", "so": "song-of-solomon",
    "is": "isaiah", "jr": "jeremiah", "lm": "lamentations", "ez": "ezekiel",
    "dn": "daniel", "ho": "hosea", "jl": "joel", "am": "amos",
    "ob": "obadiah", "jn": "jonah", "mi": "micah", "na": "nahum",
    "hk": "habakkuk", "zp": "zephaniah", "hg": "haggai", "zc": "zechariah",
    "ml": "malachi", "mt": "matthew", "mk": "mark", "lk": "luke",
    "jo": "john", "act": "acts", "rm": "romans", "1co": "1corinthians",
    "2co": "2corinthians", "gl": "galatians", "eph": "ephesians",
    "ph": "philippians", "cl": "colossians", "1ts": "1thessalonians",
    "2ts": "2thessalonians", "1tm": "1timothy", "2tm": "2timothy",
    "tt": "titus", "phm": "philemon", "hb": "hebrews", "jm": "james",
    "1pe": "1peter", "2pe": "2peter", "1jo": "1john", "2jo": "2john",
    "3jo": "3john", "jd": "jude", "re": "revelation",
}

SLUG_TO_NAME = {
    "genesis": "Genesis", "exodus": "Exodus", "leviticus": "Leviticus",
    "numbers": "Numbers", "deuteronomy": "Deuteronomy", "joshua": "Joshua",
    "judges": "Judges", "ruth": "Ruth", "1samuel": "1 Samuel",
    "2samuel": "2 Samuel", "1kings": "1 Kings", "2kings": "2 Kings",
    "1chronicles": "1 Chronicles", "2chronicles": "2 Chronicles",
    "ezra": "Ezra", "nehemiah": "Nehemiah", "esther": "Esther",
    "job": "Job", "psalms": "Psalms", "proverbs": "Proverbs",
    "ecclesiastes": "Ecclesiastes", "song-of-solomon": "Song of Solomon",
    "isaiah": "Isaiah", "jeremiah": "Jeremiah", "lamentations": "Lamentations",
    "ezekiel": "Ezekiel", "daniel": "Daniel", "hosea": "Hosea",
    "joel": "Joel", "amos": "Amos", "obadiah": "Obadiah", "jonah": "Jonah",
    "micah": "Micah", "nahum": "Nahum", "habakkuk": "Habakkuk",
    "zephaniah": "Zephaniah", "haggai": "Haggai", "zechariah": "Zechariah",
    "malachi": "Malachi", "matthew": "Matthew", "mark": "Mark",
    "luke": "Luke", "john": "John", "acts": "Acts", "romans": "Romans",
    "1corinthians": "1 Corinthians", "2corinthians": "2 Corinthians",
    "galatians": "Galatians", "ephesians": "Ephesians",
    "philippians": "Philippians", "colossians": "Colossians",
    "1thessalonians": "1 Thessalonians", "2thessalonians": "2 Thessalonians",
    "1timothy": "1 Timothy", "2timothy": "2 Timothy", "titus": "Titus",
    "philemon": "Philemon", "hebrews": "Hebrews", "james": "James",
    "1peter": "1 Peter", "2peter": "2 Peter", "1john": "1 John",
    "2john": "2 John", "3john": "3 John", "jude": "Jude",
    "revelation": "Revelation",
}


def main():
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/bible-json/json/en_kjv.json")

    if not json_path.exists():
        print(f"Error: {json_path} not found")
        print("Usage: python import_kjv_json.py [path/to/en_kjv.json]")
        sys.exit(1)

    with open(json_path, encoding="utf-8-sig") as f:
        data = json.load(f)

    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    total_files = 0
    total_verses = 0

    for book in data:
        abbrev = book["abbrev"]
        slug = ABBREV_TO_SLUG.get(abbrev)
        if not slug:
            print(f"Warning: unknown abbreviation '{abbrev}', skipping")
            continue

        book_name = SLUG_TO_NAME[slug]

        for ch_idx, chapter_verses in enumerate(book["chapters"]):
            chapter_num = ch_idx + 1
            filename = f"{slug}-{chapter_num:02d}.md"

            lines = [
                "---",
                "translation: KJV",
                f"book: {slug}",
                f"chapter: {chapter_num}",
                "---",
                "",
                f"# {book_name} {chapter_num}",
                "",
            ]

            for v_idx, verse_text in enumerate(chapter_verses):
                verse_num = v_idx + 1
                # Clean up common artifacts
                text = verse_text.strip()
                text = text.replace("{", "").replace("}", "")
                lines.append(f"{chapter_num}:{verse_num} {text}")
                lines.append("")
                total_verses += 1

            filepath = SOURCE_DIR / filename
            filepath.write_text("\n".join(lines), encoding="utf-8")
            total_files += 1

    print(f"Imported {total_verses} verses across {total_files} files")
    print(f"Output: {SOURCE_DIR}")


if __name__ == "__main__":
    main()
