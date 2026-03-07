#!/usr/bin/env python3
"""
Generate semantic embeddings for verse and passage chunks.

Uses AECai's Vanta embedding engine when available — the same production
engine used for engineering document embeddings, now applied to Scripture.
Falls back to standalone OpenAI/sentence-transformers if Vanta isn't present.

Reads chunks and produces:
- embeddings/verse_embeddings.jsonl
- embeddings/passage_embeddings.jsonl
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CHUNKS_DIR = PROJECT_ROOT / "chunks"
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"

# Wire in AECai's Vanta embedding engine if available
AECAI_ROOT = Path.home() / "aecai"
AECAI_ENGINE = AECAI_ROOT / "engine"
if AECAI_ENGINE.exists() and str(AECAI_ENGINE) not in sys.path:
    sys.path.insert(0, str(AECAI_ENGINE))
if AECAI_ROOT.exists() and str(AECAI_ROOT) not in sys.path:
    sys.path.insert(0, str(AECAI_ROOT))

VANTA_AVAILABLE = False
try:
    from vanta.vanta_embed import EmbeddingEngine, detect_backends
    VANTA_AVAILABLE = True
except ImportError:
    pass

BATCH_SIZE = 100


def load_chunks(filepath: Path) -> list[dict]:
    if not filepath.exists():
        print(f"Error: {filepath} not found. Run build_chunks.py first.")
        sys.exit(1)
    chunks = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    return chunks


def embed_with_vanta(chunks: list[dict]) -> list[dict]:
    """Generate embeddings using AECai's Vanta EmbeddingEngine."""
    engine = EmbeddingEngine(backend="auto", verbose=True)
    if not engine.available:
        print("Error: Vanta engine initialized but no backend available.")
        print("  Install: 'ollama pull nomic-embed-text' or 'pip install sentence-transformers'")
        sys.exit(1)

    print(f"  Backend: {engine.backend_name}")
    print(f"  Dimensions: {engine.dimensions}")

    texts = [c["text"] for c in chunks]
    vectors = engine.embed_batch(texts)

    stats = engine.stats
    print(f"  Generated: {stats['embeddings_generated']}")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Avg latency: {stats['avg_latency_seconds']}s")

    records = []
    for chunk, vector in zip(chunks, vectors):
        if vector is not None:
            records.append({
                "id": chunk["id"],
                "text": chunk["text"],
                "embedding": vector,
                "model": engine.backend_name,
                "dimensions": len(vector),
            })

    return records


def embed_with_openai(chunks: list[dict], model: str = "text-embedding-3-small") -> list[dict]:
    """Fallback: generate embeddings using OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai")
        sys.exit(1)

    client = OpenAI()
    texts = [c["text"] for c in chunks]
    all_vectors = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        response = client.embeddings.create(input=batch, model=model)
        for item in response.data:
            all_vectors.append(item.embedding)
        print(f"  Embedded {min(i + BATCH_SIZE, len(texts))}/{len(texts)}")

    records = []
    for chunk, vector in zip(chunks, all_vectors):
        records.append({
            "id": chunk["id"],
            "text": chunk["text"],
            "embedding": vector,
            "model": model,
            "dimensions": len(vector),
        })
    return records


def embed_with_sentence_transformers(chunks: list[dict], model_name: str = "all-MiniLM-L6-v2") -> list[dict]:
    """Fallback: generate embeddings using sentence-transformers locally."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Error: sentence-transformers not installed. Run: pip install sentence-transformers")
        sys.exit(1)

    model = SentenceTransformer(model_name)
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=BATCH_SIZE)

    records = []
    for chunk, vector in zip(chunks, embeddings):
        records.append({
            "id": chunk["id"],
            "text": chunk["text"],
            "embedding": vector.tolist(),
            "model": model_name,
            "dimensions": len(vector),
        })
    return records


def generate_embeddings(chunks: list[dict]) -> list[dict]:
    """Generate embeddings using the best available backend."""
    if VANTA_AVAILABLE:
        print("  Using AECai Vanta EmbeddingEngine (auto-detect backend)")
        return embed_with_vanta(chunks)

    backend = os.environ.get("EMBEDDING_BACKEND", "").lower()
    if backend == "openai" or os.environ.get("OPENAI_API_KEY"):
        print("  Using OpenAI API")
        return embed_with_openai(chunks)

    print("  Using sentence-transformers (local)")
    return embed_with_sentence_transformers(chunks)


def write_jsonl(filepath: Path, records: list[dict]):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    if VANTA_AVAILABLE:
        print("AECai Vanta embedding engine loaded")
        backends = detect_backends()
        print(f"  Recommended backend: {backends['recommended']}")
    else:
        print("Vanta not found — using standalone embedding backend")
        print(f"  (To enable: ensure {AECAI_ENGINE} exists)")

    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    # Verse embeddings
    verse_file = CHUNKS_DIR / "by_verse" / "verse_chunks.jsonl"
    if verse_file.exists():
        print("\nGenerating verse embeddings...")
        verse_chunks = load_chunks(verse_file)
        verse_records = generate_embeddings(verse_chunks)
        write_jsonl(EMBEDDINGS_DIR / "verse_embeddings.jsonl", verse_records)
        print(f"  Wrote {len(verse_records)} verse embeddings")
    else:
        print(f"Skipping verse embeddings: {verse_file} not found")

    # Passage embeddings
    passage_file = CHUNKS_DIR / "by_passage" / "passage_chunks.jsonl"
    if passage_file.exists():
        print("\nGenerating passage embeddings...")
        passage_chunks = load_chunks(passage_file)
        passage_records = generate_embeddings(passage_chunks)
        write_jsonl(EMBEDDINGS_DIR / "passage_embeddings.jsonl", passage_records)
        print(f"  Wrote {len(passage_records)} passage embeddings")
    else:
        print(f"Skipping passage embeddings: {passage_file} not found")

    print(f"\nDone. Embeddings generated in embeddings/")


if __name__ == "__main__":
    main()
