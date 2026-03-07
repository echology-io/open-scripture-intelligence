# Open Scripture Intelligence (OSI)

**The AI-ready Bible dataset and knowledge graph.**

An open-source project that transforms Scripture from static text into structured intelligence that AI systems can reason about.

---

## Why This Exists

Hundreds of Bible apps exist. All of them treat Scripture as a text database. None of them treat it as a knowledge system.

Most apps give users verses. This project lets apps **understand how Scripture connects**.

There is no open-source dataset that combines:

- Normalized scripture schema
- Markdown source
- Passage chunking
- Cross-reference graph
- Theological metadata (topics, entities)
- Semantic embeddings

Open Scripture Intelligence fills that gap.

---

## What This Is

A structured, multi-layer dataset built from public-domain Bible translations.

| Layer | Format | Purpose |
|---|---|---|
| Source | Markdown | Human-readable, version-controlled Scripture text |
| Canonical | JSONL | Normalized verse/chapter/book records |
| Chunks | JSONL | Verse, passage, and chapter chunks for retrieval |
| Graph | JSONL | Cross-reference edges and relationship types |
| Metadata | JSON | Topics, entities, people, places, themes |
| Embeddings | JSONL | Semantic vectors for AI search and reasoning |

---

## Repository Structure

```
open-scripture-intelligence/
  source/
    raw-markdown/          # Bible text in Markdown (one chapter per file)
  canonical/
    books.json             # Book metadata (66 books)
    verses.jsonl           # Every verse as a normalized record
    chapters.jsonl         # Chapter-level records
  chunks/
    by_verse/              # Single-verse chunks
    by_passage/            # Multi-verse passage chunks
    by_chapter/            # Full chapter chunks
  graph/
    nodes.jsonl            # Scripture graph nodes
    edges.jsonl            # Cross-reference and relationship edges
  metadata/
    topics.json            # Theological topic taxonomy
    entities.json          # People, places, concepts
  embeddings/
    verse_embeddings.jsonl
    passage_embeddings.jsonl
  scripts/
    parse_markdown.py      # Ingest Markdown -> canonical JSONL
    build_chunks.py        # Generate chunk layers
    build_graph.py         # Build cross-reference graph
  exports/
    obsidian/              # Obsidian vault export
    app/                   # App-ready export
    training/              # ML training export
  docs/
    architecture.md
    schema.md
    roadmap.md
```

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-org/open-scripture-intelligence.git
cd open-scripture-intelligence
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Parse Markdown source into canonical dataset

```bash
python scripts/parse_markdown.py
```

### 4. Build chunks

```bash
python scripts/build_chunks.py
```

### 5. Build cross-reference graph

```bash
python scripts/build_graph.py
```

---

## Schema

### Verse Record

```json
{
  "id": "web-john-3-16",
  "translation": "WEB",
  "book": "John",
  "chapter": 3,
  "verse": 16,
  "reference": "John 3:16",
  "text": "For God so loved the world, that he gave his only begotten Son, that whoever believes in him should not perish, but have eternal life.",
  "testament": "NT",
  "book_number": 43
}
```

### Passage Chunk

```json
{
  "id": "web-john-3-16-21",
  "translation": "WEB",
  "start_reference": "John 3:16",
  "end_reference": "John 3:21",
  "label": "God's love and salvation",
  "verse_ids": ["web-john-3-16", "web-john-3-17", "web-john-3-18", "web-john-3-19", "web-john-3-20", "web-john-3-21"],
  "text": "For God so loved the world..."
}
```

### Graph Edge

```json
{
  "from": "web-isaiah-53-5",
  "to": "web-1peter-2-24",
  "type": "prophecy_fulfillment",
  "label": "suffering and healing",
  "source": "openbible_crossrefs"
}
```

Full schema documentation: [docs/schema.md](docs/schema.md)

---

## Translations

Initial release uses **public domain** translations to avoid licensing restrictions:

| Translation | Status | License |
|---|---|---|
| WEB (World English Bible) | Primary | Public Domain |
| KJV (King James Version) | Supported | Public Domain |
| ASV (American Standard Version) | Planned | Public Domain |

Modern copyrighted translations (ESV, NIV, NASB) can be added via plugin layers where licensing allows.

---

## How Apps Use This

OSI is not an app. It is the **intelligence layer underneath apps**.

```
Your App (UI, users, subscriptions)
         |
    Your API layer
         |
  +----- OSI Dataset -----+
  |  Verses  |  Graph     |
  |  Chunks  |  Embeddings|
  |  Topics  |  Entities  |
  +-----------------------+
```

An app team imports this dataset into their backend (Postgres, Neo4j, vector DB) and exposes it through their own APIs. Their existing app stays the same — it just gets smarter.

See [docs/founder-pitch.md](docs/founder-pitch.md) for the full integration guide.

---

## Use Cases

- **Semantic Bible Search** — find passages by concept, not just keywords
- **Related Passage Discovery** — surface thematically connected verses
- **Prophecy Mapping** — trace OT prophecy to NT fulfillment
- **Sermon Preparation** — explore themes with AI-assisted context
- **Theological Research** — map concepts across Scripture
- **Bible Study Apps** — power "Explain This Passage" features
- **Translation Studies** — compare translations semantically
- **AI Assistants** — ground Scripture chatbots in structured data

---

## Contributing

This project is built for the community. Contributions welcome:

- Scripture text normalization
- Cross-reference data
- Topic and entity tagging
- Embedding generation
- Export format adapters
- Documentation and schema improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Roadmap

| Phase | Focus |
|---|---|
| 1 | Core dataset: normalized schema, Markdown source, verse records |
| 2 | Cross-reference graph from open datasets |
| 3 | Semantic layers: embeddings, topics, entities |
| 4 | AI interfaces: search API, graph explorer |

Full roadmap: [docs/roadmap.md](docs/roadmap.md)

---

## License

Dataset structure and tooling: MIT License

Scripture text: Public domain translations (WEB, KJV, ASV).

See [LICENSE_NOTES.md](LICENSE_NOTES.md) for details on translation-specific permissions.

---

## About

Open Scripture Intelligence is an [Echology](https://echology.dev) case study in transforming complex documents into structured knowledge systems.

The same methodology that structures Scripture can structure engineering docs, legal texts, insurance data, and any domain where knowledge is trapped inside documents.

**Scripture has shaped civilization for millennia. It's time to give AI the structure to understand it.**
