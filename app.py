#!/usr/bin/env python3
"""
OSI Explorer — Interactive GUI for Open Scripture Intelligence.

Run:
    python3 app.py
    Open http://localhost:5111
"""

import json
import math
import random
import sys
from pathlib import Path

from flask import Flask, jsonify, request, render_template_string

ECHOLOGY_SRC = Path.home() / "echology" / "src"
if ECHOLOGY_SRC.exists() and str(ECHOLOGY_SRC) not in sys.path:
    sys.path.insert(0, str(ECHOLOGY_SRC))

AECAI_ROOT = Path.home() / "aecai"
AECAI_ENGINE = AECAI_ROOT / "engine"
if AECAI_ENGINE.exists() and str(AECAI_ENGINE) not in sys.path:
    sys.path.insert(0, str(AECAI_ENGINE))
if AECAI_ROOT.exists() and str(AECAI_ROOT) not in sys.path:
    sys.path.insert(0, str(AECAI_ROOT))

SCRIPTS_DIR = Path(__file__).parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PROJECT_ROOT = Path(__file__).parent
app = Flask(__name__)

# ─── Data Loading ────────────────────────────────────────────────

def load_jsonl(filepath):
    records = []
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    return records

def load_json(filepath):
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

print("Loading OSI dataset...")
BOOKS = load_json(PROJECT_ROOT / "canonical" / "books.json")
VERSES = load_jsonl(PROJECT_ROOT / "canonical" / "verses.jsonl")
CHAPTERS = load_jsonl(PROJECT_ROOT / "canonical" / "chapters.jsonl")
EDGES = load_jsonl(PROJECT_ROOT / "graph" / "edges.jsonl")
PASSAGE_CHUNKS = load_jsonl(PROJECT_ROOT / "chunks" / "by_passage" / "passage_chunks.jsonl")

VERSE_BY_ID = {v["id"]: v for v in VERSES}
VERSE_BY_REF = {v["reference"]: v for v in VERSES}
BOOK_BY_ID = {b["id"]: b for b in BOOKS}

EDGES_FROM = {}
EDGES_TO = {}
for e in EDGES:
    EDGES_FROM.setdefault(e["from"], []).append(e)
    EDGES_TO.setdefault(e["to"], []).append(e)

BOOK_CHAPTERS = {}
for v in VERSES:
    BOOK_CHAPTERS.setdefault((v["book"], v["chapter"]), []).append(v)

EMBEDDINGS = {}
EMBED_ENGINE = None

def load_embeddings():
    global EMBEDDINGS
    emb_file = PROJECT_ROOT / "embeddings" / "verse_embeddings.jsonl"
    if emb_file.exists():
        with open(emb_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    EMBEDDINGS[rec["id"]] = rec["embedding"]
        print(f"  Loaded {len(EMBEDDINGS)} embeddings")

def get_embed_engine():
    global EMBED_ENGINE
    if EMBED_ENGINE is not None:
        return EMBED_ENGINE
    try:
        from vanta.vanta_embed import EmbeddingEngine
        engine = EmbeddingEngine(backend="auto")
        if engine.available:
            EMBED_ENGINE = engine
            return engine
    except Exception:
        pass
    return None

try:
    from scripture_entities import extract_scripture_entities, to_echology_format
    ENTITIES_AVAILABLE = True
except ImportError:
    ENTITIES_AVAILABLE = False

load_embeddings()
print(f"Loaded: {len(VERSES)} verses, {len(BOOKS)} books, {len(EDGES)} edges, {len(EMBEDDINGS)} embeddings")

# ─── Helpers ─────────────────────────────────────────────────────

def cosine_sim(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def get_cross_refs(verse_id, limit=20):
    refs = []
    for e in EDGES_FROM.get(verse_id, []):
        t = VERSE_BY_ID.get(e["to"])
        if t:
            refs.append({**t, "relationship": e["type"], "confidence": e.get("confidence", 0), "votes": e.get("votes", 0)})
    for e in EDGES_TO.get(verse_id, []):
        s = VERSE_BY_ID.get(e["from"])
        if s:
            refs.append({**s, "relationship": e["type"], "confidence": e.get("confidence", 0), "votes": e.get("votes", 0)})
    refs.sort(key=lambda r: r.get("votes", 0), reverse=True)
    return refs[:limit]

def get_passage_context(verse):
    vid = verse["id"]
    for p in PASSAGE_CHUNKS:
        if vid in p.get("verse_ids", []):
            return p
    return None

# ─── API Routes ──────────────────────────────────────────────────

@app.route("/api/random")
def api_random():
    return jsonify(random.choice(VERSES))

@app.route("/api/verse/<verse_id>")
def api_verse(verse_id):
    v = VERSE_BY_ID.get(verse_id)
    return jsonify(v) if v else (jsonify({"error": "not found"}), 404)

@app.route("/api/books")
def api_books():
    return jsonify(BOOKS)

@app.route("/api/chapters/<book_slug>")
def api_chapters(book_slug):
    chapters = sorted([c for c in CHAPTERS if c["book"] == book_slug], key=lambda c: c["chapter"])
    return jsonify([{"chapter": c["chapter"], "verse_count": c["verse_count"]} for c in chapters])

@app.route("/api/chapter/<book_slug>/<int:chapter_num>")
def api_chapter(book_slug, chapter_num):
    return jsonify(BOOK_CHAPTERS.get((book_slug, chapter_num), []))

@app.route("/api/crossrefs/<verse_id>")
def api_crossrefs(verse_id):
    return jsonify(get_cross_refs(verse_id))

@app.route("/api/passage/<verse_id>")
def api_passage(verse_id):
    v = VERSE_BY_ID.get(verse_id)
    if not v:
        return jsonify({"error": "not found"}), 404
    passage = get_passage_context(v)
    if passage:
        pvs = [VERSE_BY_ID.get(vid) for vid in passage.get("verse_ids", []) if VERSE_BY_ID.get(vid)]
        return jsonify({"passage": passage, "verses": pvs})
    return jsonify({"passage": None, "verses": [v]})

@app.route("/api/entities/<verse_id>")
def api_entities(verse_id):
    v = VERSE_BY_ID.get(verse_id)
    if not v:
        return jsonify({"error": "not found"}), 404
    if not ENTITIES_AVAILABLE:
        return jsonify({"error": "entity extraction not available"})
    ents = extract_scripture_entities(v["text"])
    return jsonify(to_echology_format(ents))

@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip().lower()
    if not q:
        return jsonify([])
    results = [v for v in VERSES if q in v["text"].lower() or q in v["reference"].lower()][:50]
    return jsonify(results)

@app.route("/api/semantic")
def api_semantic():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    if not EMBEDDINGS:
        load_embeddings()
        if not EMBEDDINGS:
            return jsonify({"error": "Embeddings still generating. Try again shortly."})
    engine = get_embed_engine()
    if not engine:
        return jsonify({"error": "No embedding engine available. Is Ollama running?"})
    q_vec = engine.embed(q)
    if not q_vec:
        return jsonify({"error": "Embedding failed"})
    scores = [(vid, cosine_sim(q_vec, vec)) for vid, vec in EMBEDDINGS.items()]
    scores.sort(key=lambda x: x[1], reverse=True)
    results = []
    for vid, sim in scores[:20]:
        v = VERSE_BY_ID.get(vid)
        if v:
            results.append({**v, "similarity": round(sim, 4)})
    return jsonify(results)

@app.route("/api/stats")
def api_stats():
    return jsonify({
        "books": len(BOOKS), "chapters": len(CHAPTERS), "verses": len(VERSES),
        "edges": len(EDGES), "passage_chunks": len(PASSAGE_CHUNKS),
        "embeddings": len(EMBEDDINGS), "entities_available": ENTITIES_AVAILABLE,
        "semantic_available": len(EMBEDDINGS) > 0,
    })

# ─── GUI ─────────────────────────────────────────────────────────

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OSI Explorer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #fafaf8; --surface: #ffffff; --surface2: #f5f5f0;
  --border: #e8e6e0; --border2: #d4d2cc;
  --text: #1a1a1a; --text2: #555; --text3: #999;
  --accent: #2563eb; --accent2: #1d4ed8;
  --warm: #92400e; --warm-bg: #fef3c7;
  --green: #059669; --green-bg: #ecfdf5;
  --purple: #7c3aed; --purple-bg: #f5f3ff;
  --rose: #e11d48; --rose-bg: #fff1f2;
  --radius: 12px; --radius-sm: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-lg: 0 4px 12px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; -webkit-font-smoothing: antialiased; }

/* Header */
.header {
  background: var(--surface); border-bottom: 1px solid var(--border);
  padding: 16px 32px; display: flex; justify-content: space-between; align-items: center;
  position: sticky; top: 0; z-index: 100; backdrop-filter: blur(12px);
}
.header-left { display: flex; align-items: center; gap: 12px; }
.logo { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
.header h1 { font-size: 0.8em; font-weight: 600; letter-spacing: 3px; color: var(--text2); text-transform: uppercase; }
.header .stats { font-size: 0.72em; color: var(--text3); font-weight: 400; }
.stat-pill { display: inline-block; padding: 2px 10px; background: var(--surface2); border-radius: 20px; margin-left: 6px; font-variant-numeric: tabular-nums; }

.container { max-width: 960px; margin: 0 auto; padding: 32px 20px; }

/* Controls */
.controls { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; align-items: center; }
.controls select, .controls input {
  padding: 9px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); color: var(--text); font-size: 0.85em;
  font-family: inherit; transition: border-color 0.2s;
}
.controls select:focus, .controls input:focus { border-color: var(--accent); outline: none; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
.controls input { flex: 1; min-width: 180px; }
.controls input::placeholder { color: var(--text3); }
.btn {
  padding: 9px 18px; border-radius: var(--radius-sm); border: 1px solid var(--border);
  background: var(--surface); color: var(--text2); font-size: 0.85em;
  font-family: inherit; cursor: pointer; transition: all 0.15s; font-weight: 500;
}
.btn:hover { border-color: var(--accent); color: var(--accent); }
.btn-primary { background: var(--accent); color: white; border-color: var(--accent); }
.btn-primary:hover { background: var(--accent2); }
.btn-ghost { border: none; background: none; color: var(--text3); }
.btn-ghost:hover { color: var(--accent); }
.divider { width: 1px; height: 24px; background: var(--border); margin: 0 4px; }

/* Verse Card */
.verse-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 32px; margin-bottom: 16px; box-shadow: var(--shadow); transition: box-shadow 0.2s;
}
.verse-card:hover { box-shadow: var(--shadow-lg); }
.verse-ref { font-size: 0.78em; font-weight: 600; color: var(--accent); letter-spacing: 0.5px; margin-bottom: 12px; text-transform: uppercase; }
.verse-text { font-family: 'Source Serif 4', Georgia, serif; font-size: 1.35em; line-height: 1.75; color: var(--text); font-weight: 400; }
.verse-meta { display: flex; gap: 12px; margin-top: 16px; }
.meta-tag { font-size: 0.7em; color: var(--text3); background: var(--surface2); padding: 3px 10px; border-radius: 20px; font-weight: 500; }

/* Toolbar */
.toolbar { display: flex; gap: 6px; margin-bottom: 24px; flex-wrap: wrap; }
.tool-btn {
  padding: 8px 16px; border-radius: 20px; border: 1px solid var(--border);
  background: var(--surface); color: var(--text2); font-size: 0.8em;
  font-family: inherit; cursor: pointer; transition: all 0.15s; font-weight: 500;
  display: flex; align-items: center; gap: 6px;
}
.tool-btn:hover { border-color: var(--accent); color: var(--accent); background: #f0f4ff; }
.tool-btn.active { border-color: var(--accent); color: var(--accent); background: #eff6ff; }
.tool-btn .badge { font-size: 0.75em; background: var(--surface2); padding: 1px 7px; border-radius: 10px; color: var(--text3); font-weight: 600; }
.tool-btn.active .badge { background: #dbeafe; color: var(--accent); }

/* Panels */
.panel {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 24px; margin-bottom: 16px; display: none; box-shadow: var(--shadow);
}
.panel.visible { display: block; animation: slideIn 0.25s ease; }
@keyframes slideIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { font-size: 0.7em; font-weight: 600; color: var(--text3); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }

/* Cross-ref items */
.ref-item { padding: 14px 0; border-bottom: 1px solid var(--surface2); cursor: pointer; transition: all 0.15s; }
.ref-item:last-child { border-bottom: none; }
.ref-item:hover .ref-reference { color: var(--accent); }
.ref-reference { font-size: 0.8em; font-weight: 600; color: var(--warm); }
.ref-text { font-family: 'Source Serif 4', Georgia, serif; font-size: 0.92em; color: var(--text2); margin-top: 4px; line-height: 1.6; }
.ref-meta { font-size: 0.7em; color: var(--text3); margin-top: 4px; display: flex; gap: 8px; }
.ref-votes { background: var(--surface2); padding: 1px 8px; border-radius: 10px; font-weight: 600; }

/* Passage */
.passage-verse { padding: 8px 16px; line-height: 1.7; font-family: 'Source Serif 4', Georgia, serif; border-left: 2px solid transparent; cursor: pointer; transition: all 0.15s; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-size: 0.95em; color: var(--text2); }
.passage-verse:hover { background: var(--surface2); }
.passage-verse.current { border-left-color: var(--accent); background: #f0f4ff; color: var(--text); }
.pv-num { color: var(--accent); font-size: 0.75em; margin-right: 8px; font-family: 'Inter', sans-serif; font-weight: 600; }

/* Entity tags */
.entity-group { margin-bottom: 14px; }
.entity-group h4 { font-size: 0.7em; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.tag { display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.8em; margin: 3px 4px 3px 0; font-weight: 500; }
.tag-theme { background: var(--green-bg); color: var(--green); }
.tag-person { background: var(--warm-bg); color: var(--warm); }
.tag-place { background: #eff6ff; color: var(--accent); }
.tag-divine { background: var(--purple-bg); color: var(--purple); }
.tag-ref { background: var(--rose-bg); color: var(--rose); }

/* Search results */
.result-item { padding: 14px 0; border-bottom: 1px solid var(--surface2); cursor: pointer; transition: all 0.15s; }
.result-item:last-child { border-bottom: none; }
.result-item:hover .sr-ref { color: var(--accent); }
.sr-ref { font-size: 0.8em; font-weight: 600; color: var(--warm); display: flex; align-items: center; gap: 8px; }
.sr-text { font-family: 'Source Serif 4', Georgia, serif; font-size: 0.92em; color: var(--text2); margin-top: 4px; line-height: 1.6; }
.sr-sim { font-size: 0.7em; background: var(--green-bg); color: var(--green); padding: 2px 8px; border-radius: 10px; font-family: 'Inter', sans-serif; font-weight: 600; }
.result-count { font-size: 0.75em; color: var(--text3); margin-bottom: 12px; font-weight: 500; }

/* Chapter view */
.cv-verse { padding: 6px 12px; line-height: 1.7; cursor: pointer; transition: all 0.15s; border-radius: var(--radius-sm); font-family: 'Source Serif 4', Georgia, serif; font-size: 0.92em; }
.cv-verse:hover { background: var(--surface2); }
.cv-verse.current { background: #eff6ff; }
.cv-num { color: var(--accent); font-size: 0.72em; margin-right: 6px; font-family: 'Inter', sans-serif; font-weight: 600; vertical-align: super; }

.empty { color: var(--text3); font-size: 0.9em; padding: 20px 0; text-align: center; }
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <div class="logo"></div>
    <h1>Open Scripture Intelligence</h1>
  </div>
  <div class="stats" id="stats"></div>
</div>

<div class="container">
  <div class="controls">
    <select id="bookSelect" onchange="loadChapters()"><option value="">Book</option></select>
    <select id="chapterSelect" onchange="loadChapter()"><option value="">Chapter</option></select>
    <button class="btn-primary btn" onclick="randomVerse()">Random</button>
    <div class="divider"></div>
    <input type="text" id="searchInput" placeholder="Keyword search..." onkeydown="if(event.key==='Enter')keywordSearch()">
    <button class="btn" onclick="keywordSearch()">Search</button>
    <div class="divider"></div>
    <input type="text" id="semanticInput" placeholder="Concept search..." onkeydown="if(event.key==='Enter')semanticSearch()">
    <button class="btn" onclick="semanticSearch()">Semantic</button>
  </div>

  <div class="verse-card" id="verseCard">
    <div class="empty">Select a book or tap Random to begin.</div>
  </div>

  <div class="toolbar" id="toolbar" style="display:none">
    <button class="tool-btn" onclick="togglePanel('crossrefs')" id="btn-crossrefs">Cross-References <span class="badge" id="crossref-count"></span></button>
    <button class="tool-btn" onclick="togglePanel('passage')" id="btn-passage">Passage</button>
    <button class="tool-btn" onclick="togglePanel('entities')" id="btn-entities">Entities</button>
    <button class="tool-btn" onclick="togglePanel('chapter')" id="btn-chapter">Chapter</button>
    <button class="tool-btn" onclick="exploreRef()" id="btn-explore">Explore</button>
  </div>

  <div class="panel" id="panel-crossrefs"><div class="panel-header">Cross-References</div><div id="crossrefs-content"></div></div>
  <div class="panel" id="panel-passage"><div class="panel-header">Passage Context</div><div id="passage-content"></div></div>
  <div class="panel" id="panel-entities"><div class="panel-header">Extracted Entities</div><div id="entities-content"></div></div>
  <div class="panel" id="panel-chapter"><div class="panel-header">Chapter</div><div id="chapter-content"></div></div>
  <div class="panel" id="panel-search"><div class="panel-header">Search Results</div><div id="search-content"></div></div>
  <div class="panel" id="panel-semantic"><div class="panel-header">Semantic Results</div><div id="semantic-content"></div></div>
</div>

<script>
let currentVerse = null, currentCrossRefs = [];
const api = async (path) => (await fetch(path)).json();

async function init() {
  const s = await api('/api/stats');
  const el = document.getElementById('stats');
  el.innerHTML = `<span class="stat-pill">${s.verses.toLocaleString()} verses</span><span class="stat-pill">${s.edges.toLocaleString()} edges</span><span class="stat-pill">${s.embeddings.toLocaleString()} embeddings</span>`;
  const books = await api('/api/books');
  const sel = document.getElementById('bookSelect');
  let t = '';
  books.forEach(b => {
    if (b.testament !== t) {
      const o = document.createElement('option'); o.disabled = true;
      o.textContent = b.testament === 'OT' ? 'Old Testament' : 'New Testament';
      o.style.fontWeight = '600'; sel.appendChild(o); t = b.testament;
    }
    const o = document.createElement('option'); o.value = b.id; o.textContent = b.name;
    sel.appendChild(o);
  });
}

async function loadChapters() {
  const book = document.getElementById('bookSelect').value;
  if (!book) return;
  const chs = await api(`/api/chapters/${book}`);
  const sel = document.getElementById('chapterSelect');
  sel.innerHTML = '<option value="">Chapter</option>';
  chs.forEach(c => { const o = document.createElement('option'); o.value = c.chapter; o.textContent = c.chapter; sel.appendChild(o); });
}

async function loadChapter() {
  const book = document.getElementById('bookSelect').value, ch = document.getElementById('chapterSelect').value;
  if (!book || !ch) return;
  const vs = await api(`/api/chapter/${book}/${ch}`);
  if (vs.length) { displayVerse(vs[0]); showPanel('chapter'); loadChapterContent(vs); }
}

function displayVerse(v) {
  currentVerse = v; hideAll();
  document.getElementById('verseCard').innerHTML = `
    <div class="verse-ref">${v.reference}</div>
    <div class="verse-text">${v.text}</div>
    <div class="verse-meta">
      <span class="meta-tag">${v.translation}</span>
      <span class="meta-tag">${v.testament === 'OT' ? 'Old Testament' : 'New Testament'}</span>
      <span class="meta-tag">${v.book_name}</span>
    </div>`;
  document.getElementById('toolbar').style.display = 'flex';
  document.getElementById('bookSelect').value = v.book;
  loadChapters().then(() => document.getElementById('chapterSelect').value = v.chapter);
}

async function randomVerse() { displayVerse(await api('/api/random')); }

function hideAll() {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('visible'));
  document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
}

function showPanel(name) {
  const p = document.getElementById(`panel-${name}`), b = document.getElementById(`btn-${name}`);
  hideAll(); p.classList.add('visible'); if (b) b.classList.add('active');
}

function togglePanel(name) {
  const p = document.getElementById(`panel-${name}`);
  if (p.classList.contains('visible')) { hideAll(); return; }
  showPanel(name);
  if (name === 'crossrefs') loadCrossRefs();
  if (name === 'passage') loadPassage();
  if (name === 'entities') loadEntities();
  if (name === 'chapter') loadFullChapter();
}

async function loadCrossRefs() {
  if (!currentVerse) return;
  const el = document.getElementById('crossrefs-content');
  el.innerHTML = '<div class="empty">Loading...</div>';
  const refs = await api(`/api/crossrefs/${currentVerse.id}`);
  currentCrossRefs = refs;
  document.getElementById('crossref-count').textContent = refs.length;
  if (!refs.length) { el.innerHTML = '<div class="empty">No cross-references found.</div>'; return; }
  el.innerHTML = refs.map(r => `
    <div class="ref-item" onclick="nav('${r.id}')">
      <div class="ref-reference">${r.reference}</div>
      <div class="ref-text">${r.text.length > 200 ? r.text.slice(0,200)+'...' : r.text}</div>
      <div class="ref-meta"><span class="ref-votes">${r.votes} votes</span><span>confidence ${r.confidence}</span></div>
    </div>`).join('');
}

async function exploreRef() {
  if (!currentVerse) return;
  if (!currentCrossRefs.length) currentCrossRefs = await api(`/api/crossrefs/${currentVerse.id}`);
  if (currentCrossRefs.length) nav(currentCrossRefs[Math.floor(Math.random() * Math.min(currentCrossRefs.length, 10))].id);
}

async function loadPassage() {
  if (!currentVerse) return;
  const el = document.getElementById('passage-content');
  el.innerHTML = '<div class="empty">Loading...</div>';
  const d = await api(`/api/passage/${currentVerse.id}`);
  if (!d.verses?.length) { el.innerHTML = '<div class="empty">No passage context.</div>'; return; }
  el.innerHTML = d.verses.map(v => `
    <div class="passage-verse ${v.id === currentVerse.id ? 'current' : ''}" onclick="nav('${v.id}')">
      <span class="pv-num">${v.verse}</span>${v.text}
    </div>`).join('');
}

async function loadEntities() {
  if (!currentVerse) return;
  const el = document.getElementById('entities-content');
  el.innerHTML = '<div class="empty">Extracting...</div>';
  const d = await api(`/api/entities/${currentVerse.id}`);
  if (d.error) { el.innerHTML = `<div class="empty">${d.error}</div>`; return; }
  const groups = [
    {k:'themes',l:'Themes',c:'theme'},{k:'divine_names',l:'Divine Names',c:'divine'},
    {k:'people',l:'People',c:'person'},{k:'places',l:'Places',c:'place'},{k:'references',l:'References',c:'ref'}];
  let html = '';
  groups.forEach(g => {
    const items = d[g.k] || [];
    if (items.length) { html += `<div class="entity-group"><h4>${g.l}</h4>${items.map(i=>`<span class="tag tag-${g.c}">${i}</span>`).join('')}</div>`; }
  });
  el.innerHTML = html || '<div class="empty">No entities found in this verse.</div>';
}

async function loadFullChapter() {
  if (!currentVerse) return;
  const vs = await api(`/api/chapter/${currentVerse.book}/${currentVerse.chapter}`);
  loadChapterContent(vs);
}
function loadChapterContent(vs) {
  document.getElementById('chapter-content').innerHTML = vs.map(v => `
    <div class="cv-verse ${currentVerse && v.id === currentVerse.id ? 'current' : ''}" onclick="nav('${v.id}')">
      <span class="cv-num">${v.verse}</span>${v.text}
    </div>`).join('');
}

async function keywordSearch() {
  const q = document.getElementById('searchInput').value.trim();
  if (!q) return;
  showPanel('search');
  const el = document.getElementById('search-content');
  el.innerHTML = '<div class="empty">Searching...</div>';
  const r = await api(`/api/search?q=${encodeURIComponent(q)}`);
  if (!r.length) { el.innerHTML = '<div class="empty">No results.</div>'; return; }
  el.innerHTML = `<div class="result-count">${r.length} results</div>` +
    r.map(v => `<div class="result-item" onclick="nav('${v.id}')"><div class="sr-ref">${v.reference}</div><div class="sr-text">${v.text}</div></div>`).join('');
}

async function semanticSearch() {
  const q = document.getElementById('semanticInput').value.trim();
  if (!q) return;
  showPanel('semantic');
  const el = document.getElementById('semantic-content');
  el.innerHTML = '<div class="empty">Generating embedding & searching...</div>';
  const r = await api(`/api/semantic?q=${encodeURIComponent(q)}`);
  if (r.error) { el.innerHTML = `<div class="empty">${r.error}</div>`; return; }
  if (!r.length) { el.innerHTML = '<div class="empty">No results.</div>'; return; }
  el.innerHTML = `<div class="result-count">${r.length} results</div>` +
    r.map(v => `<div class="result-item" onclick="nav('${v.id}')"><div class="sr-ref">${v.reference} <span class="sr-sim">${v.similarity}</span></div><div class="sr-text">${v.text}</div></div>`).join('');
}

async function nav(id) { const v = await api(`/api/verse/${id}`); if (!v.error) displayVerse(v); }

init(); randomVerse();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

if __name__ == "__main__":
    print("\n  OSI Explorer: http://localhost:5111\n")
    app.run(host="127.0.0.1", port=5111, debug=False)
