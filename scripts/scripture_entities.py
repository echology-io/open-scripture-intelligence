#!/usr/bin/env python3
"""
Scripture entity extraction — extends Echology's entity extraction pattern
to the theological domain.

Echology's decompose.entities extracts engineering standards (ASTM, ISO),
dates, and financial terms. This module applies the same regex-first,
deterministic approach to Scripture-specific entities.

Extracts:
- Scripture references (John 3:16, Genesis 1:1-3)
- Theological themes
- People, places, concepts
- Cross-reference markers

This demonstrates that Echology's entity extraction pattern is
domain-agnostic — swap the regex patterns, keep the architecture.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ── Scripture References ──────────────────────────────────────────

_BOOK_NAMES = (
    r"Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|"
    r"1\s*Samuel|2\s*Samuel|1\s*Kings|2\s*Kings|1\s*Chronicles|2\s*Chronicles|"
    r"Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|"
    r"Song\s*of\s*Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|"
    r"Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|"
    r"Haggai|Zechariah|Malachi|"
    r"Matthew|Mark|Luke|John|Acts|Romans|"
    r"1\s*Corinthians|2\s*Corinthians|Galatians|Ephesians|Philippians|"
    r"Colossians|1\s*Thessalonians|2\s*Thessalonians|"
    r"1\s*Timothy|2\s*Timothy|Titus|Philemon|Hebrews|James|"
    r"1\s*Peter|2\s*Peter|1\s*John|2\s*John|3\s*John|Jude|Revelation"
)

# Full reference: "John 3:16" or "1 Corinthians 13:4-7"
_SCRIPTURE_REF = re.compile(
    rf"\b({_BOOK_NAMES})\s+(\d+):(\d+)(?:\s*[-–]\s*(\d+))?\b"
)

# Chapter-only reference: "Genesis 1" or "Psalm 23"
_CHAPTER_REF = re.compile(
    rf"\b({_BOOK_NAMES})\s+(\d+)\b(?!:)"
)

# ── Theological Themes ────────────────────────────────────────────

_THEMES = re.compile(
    r"\b(salvation|redemption|justification|sanctification|glorification|"
    r"atonement|propitiation|reconciliation|covenant|grace|mercy|"
    r"faith|repentance|forgiveness|resurrection|eternal\s+life|"
    r"kingdom\s+of\s+God|kingdom\s+of\s+heaven|"
    r"holiness|righteousness|sin|judgment|"
    r"baptism|communion|Lord's\s+Supper|"
    r"Trinity|incarnation|ascension|second\s+coming|"
    r"predestination|election|sovereignty|providence|"
    r"spiritual\s+gifts|fruit\s+of\s+the\s+Spirit)\b",
    re.IGNORECASE,
)

# ── Named Entities ────────────────────────────────────────────────

_DIVINE_NAMES = re.compile(
    r"\b(God|LORD|Yahweh|Jehovah|Jesus|Christ|Holy\s+Spirit|"
    r"Son\s+of\s+God|Son\s+of\s+Man|Lamb\s+of\s+God|"
    r"Messiah|Immanuel|Alpha\s+and\s+Omega|"
    r"Father|Lord\s+of\s+hosts|Ancient\s+of\s+Days)\b"
)

_PEOPLE = re.compile(
    r"\b(Abraham|Isaac|Jacob|Moses|Aaron|Joshua|David|Solomon|"
    r"Elijah|Elisha|Isaiah|Jeremiah|Ezekiel|Daniel|"
    r"Peter|Paul|John|James|Matthew|Mark|Luke|"
    r"Mary|Martha|Lazarus|Stephen|Timothy|Barnabas|"
    r"Adam|Eve|Noah|Samuel|Ruth|Esther|Job|"
    r"Nicodemus|Pilate|Pharaoh|Nebuchadnezzar)\b"
)

_PLACES = re.compile(
    r"\b(Jerusalem|Bethlehem|Nazareth|Galilee|Samaria|"
    r"Egypt|Babylon|Assyria|Persia|Rome|"
    r"Jordan|Sinai|Zion|Calvary|Golgotha|"
    r"Bethany|Capernaum|Jericho|Antioch|Corinth|"
    r"Eden|Canaan|Israel|Judah|Ephesus|"
    r"Mount\s+Olivet|Sea\s+of\s+Galilee|Red\s+Sea|"
    r"Temple|Tabernacle|Ark\s+of\s+the\s+Covenant)\b"
)


@dataclass(slots=True)
class ScriptureEntities:
    """Extracted entities from Scripture text.

    Mirrors the structure of Echology's decompose.entities.Entities
    but with domain-specific fields for theological content.
    """
    references: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    divine_names: list[str] = field(default_factory=list)
    people: list[str] = field(default_factory=list)
    places: list[str] = field(default_factory=list)


def extract_scripture_entities(text: str) -> ScriptureEntities:
    """Extract structured entities from Scripture text.

    Pure regex, deterministic — same pattern as Echology's
    decompose.entities.extract_entities() but for theology.
    """
    references = []
    themes = []
    divine_names = []
    people = []
    places = []

    # Scripture references
    for m in _SCRIPTURE_REF.finditer(text):
        references.append(m.group(0).strip())
    for m in _CHAPTER_REF.finditer(text):
        references.append(m.group(0).strip())

    # Themes
    for m in _THEMES.finditer(text):
        themes.append(m.group(0).strip().lower())

    # Named entities
    for m in _DIVINE_NAMES.finditer(text):
        divine_names.append(m.group(0).strip())
    for m in _PEOPLE.finditer(text):
        people.append(m.group(0).strip())
    for m in _PLACES.finditer(text):
        places.append(m.group(0).strip())

    # Deduplicate preserving order (same pattern as Echology)
    return ScriptureEntities(
        references=list(dict.fromkeys(references)),
        themes=list(dict.fromkeys(themes)),
        divine_names=list(dict.fromkeys(divine_names)),
        people=list(dict.fromkeys(people)),
        places=list(dict.fromkeys(places)),
    )


# ── Echology Compatibility ────────────────────────────────────────

def to_echology_format(entities: ScriptureEntities) -> dict:
    """Convert to a format compatible with Echology's entity output.

    This allows OSI entity data to flow into the same downstream
    pipelines that consume Echology's engineering entity extractions.
    """
    return {
        "standards": entities.references,  # Scripture refs map to "standards"
        "dates": [],
        "financial": [],
        "references": entities.references,
        "themes": entities.themes,
        "people": entities.people,
        "places": entities.places,
        "divine_names": entities.divine_names,
    }
