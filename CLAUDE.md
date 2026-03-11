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

## Next Steps

- Integration with aecai/Qdrant vector pipeline for Scripture semantic search.
- Use as training corpus for echology model.
- decompose classification of Scripture text (authority patterns in prophetic, legal, narrative, wisdom literature).
