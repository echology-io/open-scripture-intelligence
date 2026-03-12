# open-scripture — Project Instructions

Inherits from `../CLAUDE.md`. Read that first.

## What This Is

AI-ready Bible dataset and knowledge graph. Structured Scripture intelligence for semantic search, cross-reference graphs, and AI applications. Public domain translations (WEB, KJV).

This project is the echology thesis applied to Scripture: the Logos Structure detected, classified, and made retrievable in the text where it is most explicitly present.

## Architecture

This is a **data project**, not a service. No server, no API, no runtime code.

```
canonical/          # Normalized verse/book records
  books.json        # 66 books, metadata
  verses.jsonl      # Every verse, structured

chunks/             # Retrieval-optimized text chunks
  by_verse/         # One chunk per verse
  by_passage/       # Multi-verse passage chunks
  by_chapter/       # Chapter-level chunks

graph/              # Knowledge graph
  nodes.jsonl       # Entities: people, places, themes (~4.3MB)
  edges.jsonl       # Cross-reference relationships (~50MB)
```

## Integration Points

This data is meant to be consumed by other echology systems:

- **Vector search:** Chunks can be embedded and indexed in Qdrant using the same pipeline as aecai/rbs-demo.
- **decompose:** Verse and passage text can be run through `decompose_text()` for authority/attention classification of Scripture.
- **Model training:** Structured verse data + cross-reference graph can serve as training data for the echology model.
- **Knowledge graph:** The edges dataset maps how Scripture connects — cross-references, thematic links, entity relationships. This is structure that already exists in the text, made explicit.

## Rules

- **Public domain only.** WEB and KJV translations. Do not add copyrighted translations.
- **Data integrity.** Do not modify canonical data without re-validating against source. Every verse must trace to its translation source.
- **Schema stability.** The JSONL schemas are consumed downstream. Do not change field names or structure without coordinating with consumers.
- **This is not an app.** Do not add a server, API, or frontend. This is a dataset. Other projects consume it.

## Pipeline Integration

Scripture data runs through the shared echology engine (`~/echology/engine/`) via the scripture domain module:

```bash
cd ~/echology/open-scripture
source ~/echology/aecai/.venv/bin/activate   # needs engine installed
python scripts/ingest.py --book john          # 286 passages, outputs/john.jsonl
python scripts/ingest.py --all                # all 9,971 passages
```

- `scripture_domain.py` — Domain config: 8 theological disciplines, biblical reference regex, authority signals
- `scripts/ingest.py` — Sets `ECHOLOGY_DOMAIN=scripture`, loads passages, runs through VantaPipeline
- `outputs/` — Generated JSONL results (gitignored)

### Results (Gospel of John, 286 passages, 2026-03-11)

- 264/286 passages classified with theological disciplines (gospel, law, epistle, prophecy, etc.)
- Zero AEC contamination
- Zero errors
- Discipline detection driven by KJV vocabulary: "believeth", "begotten", "son of god", "grace", "moses", "commandment"
- Entity extraction (scripture references) designed for commentary/study notes that cite passages, not the text itself

## Next Steps

- Qdrant vector indexing for Scripture semantic search
- Training corpus for echology model
- decompose classification of Scripture text (authority patterns in prophetic, legal, narrative, wisdom literature)
