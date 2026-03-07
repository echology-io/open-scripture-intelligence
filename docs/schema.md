# Schema Reference

All data formats used in the Open Scripture Intelligence dataset.

---

## Book Record

**File:** `canonical/books.json`

```json
{
  "id": "john",
  "name": "John",
  "testament": "NT",
  "book_number": 43,
  "chapters": 21,
  "category": "Gospel"
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Lowercase slug: `genesis`, `1samuel`, `john` |
| `name` | string | Display name |
| `testament` | string | `OT` or `NT` |
| `book_number` | int | 1-66 canonical order |
| `chapters` | int | Total chapter count |
| `category` | string | `Law`, `History`, `Poetry`, `MajorProphet`, `MinorProphet`, `Gospel`, `Acts`, `PaulineEpistle`, `GeneralEpistle`, `Apocalyptic` |

---

## Chapter Record

**File:** `canonical/chapters.jsonl`

```json
{
  "id": "web-john-3",
  "translation": "WEB",
  "book": "john",
  "book_name": "John",
  "chapter": 3,
  "verse_count": 36,
  "text": "Now there was a man of the Pharisees..."
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | `{translation}-{book}-{chapter}` |
| `translation` | string | Translation code |
| `book` | string | Book slug |
| `book_name` | string | Display name |
| `chapter` | int | Chapter number |
| `verse_count` | int | Number of verses |
| `text` | string | Full chapter text concatenated |

---

## Verse Record

**File:** `canonical/verses.jsonl`

```json
{
  "id": "web-john-3-16",
  "translation": "WEB",
  "book": "john",
  "book_name": "John",
  "chapter": 3,
  "verse": 16,
  "reference": "John 3:16",
  "text": "For God so loved the world, that he gave his only begotten Son, that whoever believes in him should not perish, but have eternal life.",
  "testament": "NT",
  "book_number": 43
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | `{translation}-{book}-{chapter}-{verse}` |
| `translation` | string | Translation code: `WEB`, `KJV`, `ASV` |
| `book` | string | Book slug |
| `book_name` | string | Display name |
| `chapter` | int | Chapter number |
| `verse` | int | Verse number |
| `reference` | string | Human-readable reference: `John 3:16` |
| `text` | string | Verse text |
| `testament` | string | `OT` or `NT` |
| `book_number` | int | 1-66 canonical order |

### ID Format

IDs follow the pattern: `{translation}-{book}-{chapter}-{verse}`

- Translation is lowercase: `web`, `kjv`
- Book is lowercase slug: `genesis`, `1samuel`, `song-of-solomon`
- Chapter and verse are integers (no zero-padding)

Examples:
- `web-john-3-16`
- `kjv-genesis-1-1`
- `web-1samuel-17-45`

---

## Passage Chunk

**File:** `chunks/by_passage/*.jsonl`

```json
{
  "id": "web-john-3-16-21",
  "translation": "WEB",
  "book": "john",
  "start_reference": "John 3:16",
  "end_reference": "John 3:21",
  "start_verse": 16,
  "end_verse": 21,
  "chapter": 3,
  "label": "God's love and salvation",
  "verse_ids": [
    "web-john-3-16",
    "web-john-3-17",
    "web-john-3-18",
    "web-john-3-19",
    "web-john-3-20",
    "web-john-3-21"
  ],
  "text": "For God so loved the world..."
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | `{translation}-{book}-{chapter}-{start_verse}-{end_verse}` |
| `label` | string | Short description of the passage |
| `verse_ids` | array | Ordered list of verse IDs in this passage |
| `text` | string | Concatenated verse text |

---

## Graph Node

**File:** `graph/nodes.jsonl`

```json
{
  "id": "web-john-3-16",
  "type": "verse",
  "reference": "John 3:16",
  "book": "john",
  "chapter": 3,
  "verse": 16
}
```

Node types: `verse`, `passage`, `topic`, `person`, `place`, `concept`

---

## Graph Edge

**File:** `graph/edges.jsonl`

```json
{
  "from": "web-isaiah-53-5",
  "to": "web-1peter-2-24",
  "type": "prophecy_fulfillment",
  "label": "suffering and healing",
  "confidence": 0.95,
  "source": "openbible_crossrefs"
}
```

| Field | Type | Description |
|---|---|---|
| `from` | string | Source node ID |
| `to` | string | Target node ID |
| `type` | string | Relationship type (see below) |
| `label` | string | Human-readable description |
| `confidence` | float | 0.0 to 1.0 confidence score |
| `source` | string | Data source for this edge |

### Edge Types

| Type | Description |
|---|---|
| `quotation` | Direct OT quotation in NT |
| `prophecy_fulfillment` | Prophetic passage and its fulfillment |
| `parallel` | Parallel account (Synoptic Gospels, Kings/Chronicles) |
| `thematic` | Shared theological theme |
| `allusion` | Indirect reference or echo |
| `commentary` | NT passage commenting on OT |
| `type_antitype` | OT type and NT antitype |

---

## Topic Record

**File:** `metadata/topics.json`

```json
{
  "id": "salvation",
  "label": "Salvation",
  "description": "God's work of rescuing and redeeming humanity",
  "parent": null,
  "verse_ids": ["web-john-3-16", "web-romans-10-9", "web-ephesians-2-8"]
}
```

---

## Entity Record

**File:** `metadata/entities.json`

```json
{
  "id": "jesus",
  "type": "person",
  "label": "Jesus Christ",
  "aliases": ["Jesus", "Christ", "Son of God", "Son of Man", "Lamb of God"],
  "verse_ids": ["web-john-1-1", "web-john-3-16", "web-matthew-1-1"]
}
```

Entity types: `person`, `place`, `concept`, `event`

---

## Embedding Record

**File:** `embeddings/verse_embeddings.jsonl`

```json
{
  "id": "web-john-3-16",
  "text": "For God so loved the world...",
  "embedding": [0.0123, -0.0456, 0.0789, "..."],
  "model": "text-embedding-3-small",
  "dimensions": 1536
}
```

| Field | Type | Description |
|---|---|---|
| `id` | string | Matches canonical verse/chunk ID |
| `text` | string | Source text that was embedded |
| `embedding` | array[float] | Vector values |
| `model` | string | Embedding model identifier |
| `dimensions` | int | Vector dimensionality |
