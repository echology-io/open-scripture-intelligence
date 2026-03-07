# Contributing to Open Scripture Intelligence

Thank you for your interest in contributing.

## Ways to Contribute

- **Scripture text** — help normalize public domain translations
- **Cross-references** — add or validate graph edges
- **Topics and entities** — contribute theological metadata
- **Scripts** — improve parsing, chunking, or export tools
- **Documentation** — clarify schema, add examples, fix errors
- **Integrations** — build export adapters for new platforms

## Guidelines

1. **Public domain only** — do not submit copyrighted translation text
2. **Follow the schema** — all data must conform to the formats in `docs/schema.md`
3. **One concern per PR** — keep pull requests focused
4. **Test your changes** — run the parsing pipeline to verify output
5. **Document additions** — update relevant docs when adding features

## Getting Started

```bash
git clone https://github.com/your-org/open-scripture-intelligence.git
cd open-scripture-intelligence
pip install -r requirements.txt
python scripts/parse_markdown.py
```

## Questions

Open an issue for questions, suggestions, or discussion.
