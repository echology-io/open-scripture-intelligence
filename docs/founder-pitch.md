# Open Scripture Intelligence: Integration Guide for App Founders

A concise guide for Bible app founders and Christian tech companies evaluating OSI as a backend intelligence layer.

---

## One-Line Summary

You keep your app, users, and subscriptions. This repo becomes the structured Scripture intelligence behind your premium features.

---

## What This Is

An open-source, AI-ready Bible dataset that provides:

- Every verse as a normalized record
- Passages chunked for AI retrieval
- 63,000+ cross-reference graph edges
- Theological topic and entity metadata
- Semantic embeddings for concept search

It is not an app. It is the **data layer that makes apps smarter**.

---

## What Your App Can Do With This

| Feature | Without OSI | With OSI |
|---|---|---|
| Search | Keyword matching | Semantic concept search |
| Verse view | Text + chapter nav | Related passages, themes, cross-refs |
| Study tools | Static commentary | AI-generated contextual explanations |
| Discovery | Reading plans | "Show me passages about courage" |
| Connections | Manual cross-ref lists | Typed knowledge graph (prophecy, parallel, thematic) |

---

## How Integration Works

### Step 1: Clone the dataset

```bash
git clone https://github.com/your-org/open-scripture-intelligence.git
```

### Step 2: Load into your storage

Map OSI data to your existing infrastructure:

| OSI Layer | Your Store | Why |
|---|---|---|
| `canonical/verses.jsonl` | PostgreSQL / SQLite | Structured queries |
| `graph/edges.jsonl` | Neo4j / Memgraph | Relationship traversal |
| `embeddings/*.jsonl` | pgvector / Qdrant / Pinecone | Semantic search |
| `metadata/topics.json` | PostgreSQL / Elasticsearch | Faceted filtering |

### Step 3: Build internal endpoints

Example API routes your team creates on top of OSI data:

```
GET  /scripture/reference/john-3-16
GET  /scripture/passages?topic=faith
GET  /scripture/related?reference=romans-5-3
GET  /scripture/search?q=hope+in+suffering
GET  /scripture/graph?reference=isaiah-53-5
```

### Step 4: Connect to your app UI

Your front end stays the same. New features are powered by the new endpoints.

---

## Architecture After Integration

```
Mobile App / Web App
         |
    Your API Layer
         |
+--------+---------+--------+--------+
| Postgres         | Neo4j  | Vector | Redis  |
| verses, topics   | edges  | embed  | cache  |
+--------+---------+--------+--------+
         |
   OSI Dataset (imported)
```

---

## Example: "Related Passages" Feature

User opens **Romans 5:3** in your app.

**Your backend does:**

1. Query verse table for Romans 5:3 text and metadata
2. Query graph edges for connected passages
3. Query passage chunks for broader context
4. Query vector index for semantically similar passages
5. Return ranked results

**API response:**

```json
{
  "reference": "Romans 5:3",
  "text": "Not only that, but we rejoice in our sufferings...",
  "related_passages": [
    {
      "reference": "James 1:2-4",
      "relationship": "parallel_theme",
      "reason": "testing produces steadfastness"
    },
    {
      "reference": "1 Peter 1:6-7",
      "relationship": "parallel_theme",
      "reason": "faith refined by trial"
    },
    {
      "reference": "Hebrews 12:11",
      "relationship": "thematic_similarity",
      "reason": "discipline yields righteousness"
    }
  ]
}
```

Your UI renders this as a "Related Passages" card on the verse screen.

---

## Example: End User Story

**Daniel** is a Christian entrepreneur preparing to lead a weekly men's group.

He opens his Bible app and reads Romans 5:3.

**Today (without OSI):**
- He sees the verse text
- He searches "suffering" — gets keyword results
- He spends 2 hours cross-referencing commentaries

**With OSI powering the app:**
- He taps "Related Passages" and instantly sees James 1:2, 1 Peter 1:6, Hebrews 12:11
- He taps "Explain Theme" and sees: *"Scripture consistently connects suffering with the strengthening of faith. Trials produce perseverance, maturity, and hope."*
- He taps "Scripture Map" and sees a visual graph connecting the passages
- He prepares his study in 10 minutes

---

## Minimum Viable Integration

You don't need to adopt everything at once.

**Start with just:**
1. `canonical/verses.jsonl` — normalized verse data
2. `chunks/by_passage/` — passage-level chunks
3. `graph/edges.jsonl` — cross-reference relationships

That alone enables:
- Related passage suggestions
- Smarter search
- Contextual verse linking

**Add later:**
- Embeddings for semantic search
- Topics for filtered exploration
- Entities for people/place navigation
- Graph visualization

---

## What You Gain

| Benefit | Detail |
|---|---|
| Faster development | Skip years of data normalization work |
| Better features | Ship semantic search, graph features, AI tools |
| Lower risk | Build on an open, documented, community-maintained dataset |
| Ecosystem leverage | As the dataset improves, your app improves |
| Differentiation | Offer intelligence, not just text retrieval |

---

## Who This Is For

- Bible study apps
- Sermon preparation platforms
- Christian AI assistants
- Theological education tools
- Church management platforms with study features
- Christian publishing platforms

---

## Who Built This

Open Scripture Intelligence is a project by [Echology](https://echology.dev), demonstrating how complex documents can be transformed into structured knowledge systems that AI can reason about.

---

## Next Steps

1. Clone the repo and explore the dataset
2. Load `verses.jsonl` into your dev database
3. Try the graph edges — query related passages for any verse
4. Reach out to discuss integration support

**Contact:** [your contact info]
