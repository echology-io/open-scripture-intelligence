# Roadmap

## Phase 1: Core Dataset

- [ ] Import WEB (World English Bible) Markdown source
- [ ] Build parse_markdown.py pipeline
- [ ] Generate `books.json` (66 books)
- [ ] Generate `verses.jsonl` (31,000+ verses)
- [ ] Generate `chapters.jsonl`
- [ ] Validate schema consistency
- [ ] Add KJV as second translation

## Phase 2: Cross-Reference Graph

- [ ] Import Open Bible cross-reference dataset
- [ ] Normalize edge format to OSI schema
- [ ] Classify edge types (quotation, prophecy, thematic, parallel)
- [ ] Generate `graph/nodes.jsonl`
- [ ] Generate `graph/edges.jsonl`
- [ ] Validate bidirectional consistency

## Phase 3: Semantic Layers

- [ ] Generate verse-level embeddings
- [ ] Generate passage-level embeddings
- [ ] Build topic taxonomy (`metadata/topics.json`)
- [ ] Extract entities (`metadata/entities.json`)
- [ ] Link topics and entities to verse IDs
- [ ] Validate embedding quality with test queries

## Phase 4: AI Interfaces

- [ ] Reference semantic search API (FastAPI)
- [ ] Graph query endpoint
- [ ] Obsidian vault export script
- [ ] Sample app integration demo
- [ ] Documentation for common integration patterns

## Phase 5: Community and Ecosystem

- [ ] CONTRIBUTING.md and contribution guidelines
- [ ] CI validation for schema consistency
- [ ] Additional translation support (ASV, Darby)
- [ ] Community topic/entity contributions
- [ ] Plugin architecture for custom metadata layers
