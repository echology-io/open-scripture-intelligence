"""
Scripture Domain Data — Biblical Text Analysis
===============================================
Pure data module. NO imports from engine modules.

All Scripture-specific patterns, discipline keywords, collections,
and configuration consolidated following the same seam pattern as aec.py.
"""

import logging

logger = logging.getLogger("domain.scripture")

# ═══════════════════════════════════════════════════════════════════
# SEAM 1: Entity patterns — Biblical references
# ═══════════════════════════════════════════════════════════════════

ENTITY_PATTERNS = {
    "scripture_reference": (
        r"\b(?:"
        r"(?:[123]\s*)?"
        r"(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth"
        r"|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs"
        r"|Ecclesiastes|Song\s+of\s+Solomon|Isaiah|Jeremiah|Lamentations"
        r"|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum"
        r"|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi"
        r"|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians"
        r"|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus"
        r"|Philemon|Hebrews|James|Peter|Jude|Revelation)"
        r"|(?:Gen|Exod?|Lev|Num|Deut|Josh|Judg|Sam|Kgs|Chr|Neh|Esth"
        r"|Psa?|Prov|Eccl|Isa|Jer|Lam|Ezek|Dan|Hos|Mic|Hab|Zeph|Hag"
        r"|Zech|Mal|Matt?|Mrk|Lk|Jn|Rom|Cor|Gal|Eph|Phil|Col|Thess?"
        r"|Tim|Tit|Phlm|Heb|Jas|Pet|Rev)\.?"
        r")\s+\d{1,3}(?:\s*:\s*\d{1,3}(?:\s*[-–]\s*\d{1,3})?)?"
    ),
}

ENTITY_VALIDATORS = {
    "scripture_reference": lambda v: len(v) >= 5 and any(c.isdigit() for c in v),
}

# ═══════════════════════════════════════════════════════════════════
# SEAM 2: Standard patterns — not applicable to Scripture
# ═══════════════════════════════════════════════════════════════════

STANDARD_PATTERNS = {}

# ═══════════════════════════════════════════════════════════════════
# SEAM 3: Discipline patterns — theological categories
# ═══════════════════════════════════════════════════════════════════

DISCIPLINE_PATTERNS = {
    "law": [
        "law", "commandment", "statute", "ordinance", "decree",
        "covenant", "torah", "moses", "thou shalt", "transgression",
        "unclean", "clean", "offering", "sacrifice", "tithe",
    ],
    "prophecy": [
        "prophecy", "prophet", "oracle", "vision", "thus saith",
        "the lord says", "woe", "judgment", "remnant", "restore",
        "foretold", "fulfilled", "desolation", "appointed time",
    ],
    "poetry": [
        "psalm", "song", "praise", "selah", "meditation",
        "wisdom", "vanity", "folly", "proverb", "riddle",
        "lament", "rejoice", "thanksgiving", "blessing",
    ],
    "gospel": [
        "gospel", "jesus", "christ", "messiah", "kingdom",
        "parable", "miracle", "disciple", "apostle", "preach",
        "baptize", "crucify", "resurrection", "salvation",
        "believeth", "begotten", "son of god", "son of man",
        "follow me", "everlasting life", "eternal life",
        "condemned", "forgive", "repent", "saviour",
    ],
    "epistle": [
        "epistle", "letter", "grace", "faith", "church",
        "brethren", "doctrine", "sanctification", "justification",
        "righteousness", "edify", "exhort", "admonish",
    ],
    "apocalyptic": [
        "apocalypse", "revelation", "vision", "beast", "seal",
        "trumpet", "throne", "angel", "judgment", "tribulation",
        "new heaven", "new earth", "end times", "second coming",
    ],
    "history": [
        "king", "kingdom", "reign", "battle", "conquest",
        "exile", "captivity", "temple", "tabernacle", "tribe",
        "genealogy", "chronicle", "inheritance", "land",
    ],
    "wisdom": [
        "wisdom", "understanding", "knowledge", "instruction",
        "discernment", "prudence", "counsel", "fear of the lord",
        "righteous", "wicked", "fool", "wise",
    ],
}

# ═══════════════════════════════════════════════════════════════════
# SEAM 6: Collections — Qdrant schema for Scripture
# ═══════════════════════════════════════════════════════════════════

COLLECTIONS = {
    "scripture": {
        "description": "Semantic units from biblical text",
        "payload_indices": [
            "book", "chapter", "testament", "category",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════
# SEAM 7: Extra action signals — authority markers
# ═══════════════════════════════════════════════════════════════════

EXTRA_ACTION_SIGNALS = [
    (r"\bthus saith the lord\b", 4.0, "authority"),
    (r"\bthou shalt\b", 3.5, "commandment"),
    (r"\bthou shalt not\b", 4.0, "commandment"),
    (r"\bcommandment\b", 3.0, "commandment"),
    (r"\bwarning\b", 2.5, "warning"),
    (r"\bpromise\b", 2.5, "promise"),
    (r"\bblessed\b", 2.0, "blessing"),
    (r"\bwoe\b", 3.0, "warning"),
]

# ═══════════════════════════════════════════════════════════════════
# SEAM 8: Document types & standard reference patterns
# ═══════════════════════════════════════════════════════════════════

EXTRA_DOCUMENT_TYPES = {
    "verse",
    "passage",
    "chapter",
    "psalm",
    "epistle",
    "prophecy",
    "gospel_narrative",
    "parable",
    "genealogy",
}

import re as _re

STANDARD_REFERENCE_PATTERNS = {
    "bible_reference": _re.compile(
        r"\b(?:[123]\s*)?(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth"
        r"|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs"
        r"|Ecclesiastes|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel"
        r"|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah"
        r"|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians"
        r"|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus"
        r"|Philemon|Hebrews|James|Peter|Jude|Revelation)\s+\d{1,3}(?:\s*:\s*\d{1,3})?"
    ),
}

USE_AEC_SCHEMA_EXTENSION = False

# ═══════════════════════════════════════════════════════════════════
# SEAM 10: Certification disclaimer
# ═══════════════════════════════════════════════════════════════════

CERTIFICATION_DISCLAIMER = (
    "REFERENCE ONLY. This analysis is generated by automated text processing "
    "and does not constitute theological interpretation, doctrinal authority, "
    "or scholarly commentary. All classifications and structural analysis "
    "should be reviewed by qualified biblical scholars. Source text is the "
    "King James Version (public domain)."
)
