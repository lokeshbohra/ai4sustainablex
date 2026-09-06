# 🌱 ai4sustainablex

**ESG report drafts from your own documents. Every claim cited. Every gap flagged. Nothing uploaded.**

[![License: BUSL 1.1](https://img.shields.io/badge/License-BUSL--1.1-orange.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Node.js Optional](https://img.shields.io/badge/node.js-18+-optional-orange.svg)](https://nodejs.org/)

> Run proprietary ESG documents through **your** machine.
> Get a structured, framework-aligned **first draft** — with source citations on every claim
> and **data gaps flagged** instead of guessed.
> Then decide: **DIY-refine it for free**, or **upgrade to SustainableX validation** for board-ready rigor.

---

## 📖 Table of Contents

- [What this does that generalist AI tools won't](#what-this-does-that-generalist-ai-tools-wont)
- [See the output before you install](#see-the-output-before-you-install)
- [What you get](#what-you-get)
- [How it works](#how-it-works)
- [Free vs. SustainableX Validation](#free-vs-sustainablex-validation)
- [Trust & privacy](#trust--privacy)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Report Templates](#report-templates)
- [LLM Providers](#llm-providers)
- [Architecture](#architecture)
- [Extending (Connectors & Plugins)](#extending-connectors--plugins)
- [System Requirements](#system-requirements)
- [FAQ](#faq)
- [Support](#support)
- [License](#license)

---

## What this does that generalist AI tools won't

1. **Shows its work** — every claim is matched to your PDFs and given a confidence verdict. No confident paragraph without a receipt.
2. **Admits what it can't verify** — if the data isn't in your documents, it says so. You get a gap list, not a hallucinated number.
3. **Stays out of your data** — indexing and generation run on your machine. A free tier proves we're solving the problem, not locking you in.

---

## See the output before you install

- **Basic ESG report** — a structured first draft with per-claim citations and inline gap flags: [`examples/sample-esg-report.md`](examples/sample-esg-report.md)
- **What the engine flagged** — the "insufficient data" notes and claim-level verdicts that ship inside every draft: [`examples/gap-flags-and-verdicts.md`](examples/gap-flags-and-verdicts.md)
- **The redline** — what a human ESG consultant would change before a draft goes to a board: [`examples/consultant-redline.md`](examples/consultant-redline.md)

Run it on a real folder in 10 minutes and judge for yourself.

---

## What you get

| Outcome | What it means |
|----------|---------------|
| 📄 **A structured first draft** | Scaffolded to GRI / CDP / SBTi-style structure — plus IFRS S1/S2, CSRD/ESRS, CSDDD, BRSR and more in the library — grounded in **your** disclosures, not boilerplate |
| 🔖 **Citations on every claim** | Each supported statement carries the source filename and page. Verify the report against your own files in minutes |
| 🚩 **Data gaps flagged, not hidden** | Missing Scope 1 breakdown? No 2023 baseline? The draft says so, in place, instead of inventing a number to look complete |
| 🔒 **Local by default** | Indexing, search and generation run on your machine (Ollama). Cloud LLMs are optional and opt-in — your files never leave unless you choose a cloud model |
| 🛡️ **Claims scored against sources** | A grounding score (0–100) and per-claim verdicts show how much of the report is actually backed by your files |
| ✍️ **Your call on finishing** | The free tier is a complete workflow. SustainableX Validation adds human and regulatory rigor when a board or regulator is the audience |

---
## How it works

1. **Point it at a folder.** Your PDFs, DOCX, spreadsheets, slides, text files — the folder you choose, and nothing outside it.
2. **It indexes locally.** Documents are chunked, embedded, and stored on your machine. No upload, no cloud index.
3. **Ask or scaffold.** Ask questions against your own files, or pick a report structure (Basic ESG, GHG emissions, compliance checklist, and more).
4. **You get a draft with receipts.** A first draft where every claim is cited to a source file + page, every gap is flagged in place, and a grounding score tells you how much is actually backed by your documents.

**Then the hard part is your decision, not our software:**

- **Path 1 — DIY (free, forever).** Take the draft, fill the flagged gaps from your own records, and review it in your normal workflow. Nothing about the tool stops you.
- **Path 2 — SustainableX Validation.** When the audience is a regulator or a board, upgrade. Our team pressure-tests your claims against the regulation and against peer disclosures, and returns a package that shows *what changed and why*.

---

## Free vs. SustainableX Validation

| Tier | Price | What you get |
|------|-------|--------------|
| **Draft (free)** | $0 | Structured drafts from your own documents (4 core templates), citations + gap flags, local or BYO-LLM, search & Q&A. A complete workflow, forever. |
| **Template library** | $99 one-time | The framework library: GRI 2021, SBTi, CDP, IFRS S1/S2, CSRD/ESRS, CSDDD, AFOLU/FLAG/REDD+, BRSR (+ Core Assurance, SME-lite), Supply-Chain DD, Africa Climate-Gender, and task outputs. |
| **Validation** | from $500/report · or $200/mo | Everything above, plus SustainableX team review: claim-level confidence scoring · ESRS / IFRS S1/S2 data-point checks · peer benchmarking · a consultant redline with methodology notes. |
| **Enterprise / OEM** | Contact us | SLA, unlimited seats, white-label, embedding. |

Free tier proves we solve the problem. Validation tier proves we're serious about compliance.

---

## Trust & privacy

### What we deliberately don't fake

- **"Insufficient data" is a feature.** If the context doesn't contain it, the report says so and logs it as a gap — it never invents a number to make the section look complete.
- **Every claim is traceable.** Reports carry filename + page citations; unsupported claims get a severity flag, not a confident paragraph.
- **Free drafts are not assurance-ready**, and we don't pretend otherwise. If you need regulatory-grade rigor, that's the Validation tier.
- **Scanned PDFs need OCR** (not bundled); the tool only reads what you point it at.

### How claims are scored (anti-hallucination engine)

Every generated answer passes through a claims verifier that:

- **Extracts claims** from the draft
- **Matches each claim** against your source documents
- **Scores confidence** using exact-phrase and term overlap
- **Flags unsupported claims** with a severity warning
- **Writes citations** for supported claims
- **Produces a grounding score (0–100)** for the overall report

Verdicts: `highly_reliable` / `mostly_reliable` / `moderate` / `low_confidence` / `unreliable`.

Run it manually (optional, needs Node.js):

```bash
node anti_hallucination.js --answer "The company reduced emissions by 15%" \
    --sources "Source 1 text with 15% figure|Source 2 text about emissions"
```

### Local processing & data boundaries

- **Only folders you specify** are indexed — no recursive system scanning.
- Indexes and config live under `~/.ai4sustainablex/` and `~/ai4sustainablex_workspace/` on your machine.
- **API keys are stored locally and never transmitted** except to the service endpoints you configure.
- With Ollama (default) the whole pipeline runs offline — no internet needed after model download.
- Cloud LLM providers (OpenAI, Claude, etc.) are optional; if you use one, only the prompt + retrieved context go to that provider.

### Honest about boundaries

- Reports are **AI-generated drafts** — the grounding score and gap flags tell you exactly what needs a human eye. They are not assurance-ready outputs.
- Template structures follow current frameworks but may not reflect the latest amendments; verify before filing.
- No real-time collaboration — this is a single-user local tool.
- The Africa Climate template provides structural analysis; ground-truth data must be supplied by you.

---
## Quick Start

### Option A: One-Command Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/install.sh | bash
```

The installer detects your OS, checks Python 3.10+, installs Ollama (the local AI runtime), pulls the default model (`llama3.2:1b`) in the background, installs dependencies into a virtual environment, and starts the backend server. Takes 3–5 minutes.

### Option B: Manual Install

```bash
git clone https://github.com/lokeshbohra/ai4sustainablex.git
cd ai4sustainablex

# Virtual environment + dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the backend
nohup venv/bin/python main.py > esg.log 2>&1 &
```

### Your First 3 Commands

```bash
# 1. Interactive setup (accept ToS, choose your document folder, configure providers)
python cli.py setup

# 2. Index a folder of ESG documents
python cli.py init ~/Documents/ESG_Reports

# 3. Ask a question against your own files — every answer cites sources
python cli.py ask "What are our Scope 1 and 2 emissions for FY2024?"
```

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/uninstall.sh | bash
```

Stops the server and removes only ai4sustainablex's own files (app, `~/ai4sustainablex_workspace`, `~/.ai4sustainablex`, the downloaded model after confirmation). Your documents and other Ollama models are untouched.

---

## CLI Reference

```bash
# ─── Setup & Status ───────────────────────────────
python cli.py setup                    # Interactive first-time setup wizard
python cli.py status                   # Show system status and health
python cli.py ui                       # Open web interface / API docs (localhost:8000)

# ─── Document Indexing ────────────────────────────
python cli.py init ~/Documents/ESG     # Index a folder of ESG documents
python cli.py init                      # Use the folder from your config

# ─── Q&A / Search ─────────────────────────────────
python cli.py ask "What are our Scope 1 emissions?"
python cli.py search "renewable energy targets"          # Hybrid search
python cli.py search "supply chain emissions" --web      # Include web search
python cli.py search "biodiversity" --search-type bm25   # Keyword-only

# ─── Report Generation ────────────────────────────
python cli.py report                                   # Default ESG report
python cli.py report -t ghg-emissions -c "Acme Corp" -p "FY2024"
python cli.py report -t esg-report-basic -c "Acme Corp" -p "FY2024" -f pdf
python cli.py report -t esg-report-basic -c "Acme Corp" -p "FY2024" -f docx

# ─── Templates ────────────────────────────────────
python cli.py templates                # List all templates
python cli.py templates --free         # Free templates only
python cli.py templates -s GRI         # Search by keyword
python cli.py templates -c SBTi        # Filter by category

# ─── LLM Providers ────────────────────────────────
python cli.py providers list           # List providers
python cli.py providers models         # List Ollama models
python cli.py providers switch openai --model gpt-4o

# ─── Knowledge Graph ──────────────────────────────
python cli.py graph stats              # Graph statistics
python cli.py graph entity "Scope 1"   # Query an entity

# ─── Connectors ───────────────────────────────────
python cli.py connectors sx            # SustainableX API status
python cli.py connectors search        # Search engine status
```

### API Endpoints

All commands above call a local REST API. Full Swagger docs at `http://localhost:8000/docs`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/index` | Index a folder of ESG documents |
| `POST` | `/search` | Hybrid BM25 + dense search |
| `POST` | `/chat` | RAG-enhanced Q&A |
| `POST` | `/generate_report` | Generate an ESG report |
| `GET`  | `/templates` | List available templates |
| `POST` | `/providers/switch` | Switch LLM provider |
| `GET`  | `/graph/entity/{entity}` | Query the knowledge graph |
| `GET`  | `/status` | Full system status |
| `GET`  | `/health` | Health check |

---
## Report Templates

### Core templates — always free (4)

| Template ID | Name | What it scaffolds |
|-------------|------|-------------------|
| `esg-report-basic` | Basic ESG Report | Executive summary, E/S/G performance, KPIs, materiality, targets, methodology |
| `ghg-emissions` | GHG Emissions Analysis | GRI 305-style: scopes 1–3, intensity, baselines, targets, verification |
| `sustainability-brief` | Sustainability Brief | Board-ready summary: highlights, material issues, risks, commitments |
| `sme-readiness` | SME ESG Readiness Assessment | Current practices, data readiness, quick wins, 3-year roadmap |

### Framework library — Template library / Validation tier

The full framework library unlocks with a one-time Template Library key ($99) or is included with SustainableX Validation:

| Template ID | Name | Framework |
|-------------|------|-----------|
| `carbon-footprint` | Carbon Footprint Analysis | CDP |
| `compliance-checklist` | ESG Compliance Checklist | Multi |
| `gri-full-report` | GRI Standards Full Report | GRI 2021 |
| `sbcds-targets` | SBTi Target Setting & Validation | SBTi |
| `cdp-disclosure` | CDP Climate Change Disclosure | CDP |
| `ifrs-s1-s2` | IFRS S1 & S2 Sustainability Disclosures | ISSB |
| `csrd-esrs` | CSRD / ESRS Compliance Report | ESRS |
| `csddd-due-diligence` | CSDDD Due Diligence Report | CSDDD |
| `supply-chain-due-diligence` | Supply Chain Due Diligence | CSDDD |
| `afolu-flag-redd` | AFOLU, FLAG & REDD+ Project Report | VCS/CCB |
| `africa-climate-gender` | Africa Climate, Gender & Livelihoods Nexus | Multi |
| `brsr-report` | BRSR Comprehensive Report (India) | BRSR |
| `brsr-core-assurance` | BRSR Core Assurance | BRSR |
| `sme-brsr-lite` | BRSR Lite for SMEs | SME |
| `social-media-post` | Social Media ESG Post | Task |
| `newsletter` | ESG Newsletter | Task |
| `stakeholder-disclosure` | Stakeholder Disclosure | Task |

Use the library when a specific framework deadline or regulator is the audience; use Validation when the output must hold up to scrutiny.

---

## LLM Providers

The provider package ships **12 LLM providers** — one fully local, the rest cloud. The default is Ollama, so the whole pipeline runs offline with no API key.

| Provider | Type | Default Model | API Key | Notes |
|----------|------|---------------|---------|-------|
| **Ollama** | Local | `llama3.2:1b` | None | Default. Fully offline. Runs on CPU. |
| **OpenAI** | Cloud | `gpt-4o-mini` | Required | Highest writing quality |
| **Anthropic** | Cloud | `claude-3-5-sonnet` | Required | Strong on long reports |
| **DeepSeek** | Cloud | `deepseek-chat` | Required | Cost-effective |
| **Gemini** | Cloud | `gemini-2.0-flash` | Required | Good structured output |
| **Kimi K2** | Cloud | `moonshot-v1-8k` | Required | Large context window |

Additional providers in the package: **Groq, xAI (Grok), OpenRouter, GLM (Zhipu), Qwen, Sakana Fugu**.

Cloud keys are **optional** and never required. If you use a cloud provider, only your prompt and retrieved context go to that provider — your documents are never uploaded for indexing.

```bash
python cli.py providers list                                  # List all providers
python cli.py providers switch openai --model gpt-4o          # Switch provider
python cli.py providers switch ollama --model llama3.2:3b     # Switch model

# Pull other local models, then switch to them
ollama pull llama3.2:3b      # 3B (~2GB)
ollama pull mistral          # 7B (~4.1GB)
ollama pull deepseek-r1:7b   # With reasoning
```

---
## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ai4sustainablex (your machine)               │
│                                                                  │
│  ┌───────────┐  ┌───────────┐  ┌────────────┐  ┌─────────────┐  │
│  │  CLI      │  │  GUI      │  │  Setup     │  │  Plugin     │  │
│  │  (Click)  │  │  (Electron)│  │  Wizard    │  │  Connectors │  │
│  └─────┬─────┘  └─────┬─────┘  └─────┬──────┘  └──────┬──────┘  │
│        └──────────────┼──────────────┼─────────────────┘        │
│                       ▼              ▼                           │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (port 8000)                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │ Hybrid RAG   │  │ Knowledge    │  │ Report Builder   │  │  │
│  │  │ (BM25+FAISS) │  │ Graph        │  │ + Templates      │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │  │
│  │              ┌─────────────────────────────┐                │  │
│  │              │ Claims verifier (Node.js)   │                │  │
│  │              │ citations · verdicts · score │                │  │
│  │              └─────────────────────────────┘                │  │
│  └────────────────────────┬────────────────────────────────────┘  │
│                           ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  LLM: Ollama (local) · or your own cloud key (opt-in)      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                           ▼                                       │
│               ┌───────────────────────────────┐                   │
│               │  Local File System            │                   │
│               │  • Your documents (read-only)  │                   │
│               │  • Vector DB (FAISS)           │                   │
│               │  • Knowledge Graph             │                   │
│               │  • Generated Reports           │                   │
│               └───────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.10+ · FastAPI |
| CLI | Click |
| GUI (optional) | Electron |
| Local LLM | Ollama (`llama3.2:1b` default) |
| Retrieval | Hybrid BM25 + dense FAISS, weighted RRF |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`, 50+ languages) |
| Knowledge graph | NetworkX + entity extraction |
| Claims verifier | Node.js (`anti_hallucination.js`) |
| Report output | Markdown · PDF (WeasyPrint) · DOCX |

---

## Extending (Connectors & Plugins)

Connectors inherit a small `BaseConnector` interface (`authenticate()`, `search()`, `get_templates()`, `health_check()` …), so adding one is a single class.

### SustainableX API & Data

- **Template library** — serves core templates locally; the framework library unlocks via the SustainableX API key (see [Free vs. SustainableX Validation](#free-vs-sustainablex-validation)).
- **ESG data & frameworks** — framework metadata, metrics, and standards from the SustainableX data API.

### Search engines

| Engine | Type | API Key | Notes |
|--------|------|---------|-------|
| **DuckDuckGo** | Web search | None | Default. Always enabled. |
| **Tavily** | Semantic web search | `TAVILY_API_KEY` | Optimized for research |

Engines can run in parallel to cross-reference results during report generation.

### Knowledge graph

The graph links entities across your documents (GHG, CO2, GRI, SBTi, CDP, metrics, frameworks). Reports automatically pull related entities and connected documents to enrich context — and the graph is a quick way to see cross-document connections you might have missed.

### GUI (optional)

For users who prefer a desktop interface instead of the terminal:

```bash
cd gui
npm install
npm start
```

The Electron shell spawns the Python backend and loads the web UI at `http://localhost:8000` with a visual search bar, report buttons, and system status.

---
## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | macOS 13+ / Ubuntu 20.04+ / Windows 10+ (WSL) | Latest |
| RAM | 8 GB | 16 GB+ |
| Disk | 4 GB free | 10 GB+ (multiple models) |
| Python | 3.10+ | 3.11+ |
| Ollama | Latest | Latest |
| Node.js | 18+ (optional — claims verifier) | 20+ |

The default model (`llama3.2:1b`) uses ~1.3 GB and runs comfortably on 8 GB RAM with CPU-only inference.

---

## FAQ

**Q: Is my data safe?**
A: Yes. Indexing and default generation are local. No documents, queries, or indexed data leave your machine unless you explicitly configure a cloud LLM provider. See [DISCLAIMER.md](DISCLAIMER.md).

**Q: Do I need an internet connection?**
A: Only for installation and the initial model download. After that, Ollama-based usage works fully offline. Cloud providers require internet by nature.

**Q: What if the draft says "insufficient data"?**
A: That's the tool working. It means the number isn't in the documents you pointed it at — add the source document and re-index, or fill it from your records. It will not invent it for you.

**Q: What's the smallest model I can use?**
A: `llama3.2:1b` (~1.3 GB). Fast, runs on CPU. Pull it with `ollama pull llama3.2:1b`; you can switch models any time.

**Q: Can I use my own GGUF model files?**
A: Yes — create an Ollama Modelfile pointing to your GGUF, run `ollama create my-model -f Modelfile`, then `python cli.py providers switch ollama -m my-model`.

**Q: How do I get the framework template library or Validation?**
A: See [Free vs. SustainableX Validation](#free-vs-sustainablex-validation). The one-time Template Library key and Validation are available via https://sustainablex.in — email info@sustainablex.in with your use case.

**Q: Does it support non-English documents?**
A: The embedding model supports 50+ languages; LLM language support depends on the model you choose.

**Q: Can I run it on a server for my team?**
A: The FastAPI backend can sit behind a reverse proxy with authentication, but this is a single-user tool by design — concurrent users need separate indexes.

**Q: How do I update ai4sustainablex?**
A: Re-run the installer or `git pull` in the app folder, then `pip install -r requirements.txt --upgrade`.

---

## Support

- **🌐 Website**: https://sustainablex.in
- **📧 Email**: info@sustainablex.in
- **🐛 Issues**: https://github.com/lokeshbohra/ai4sustainablex/issues
- **💬 Discussions**: https://github.com/lokeshbohra/ai4sustainablex/discussions
- **📖 API docs**: `http://localhost:8000/docs` (when running)

---

## License

ai4sustainablex is licensed under the **Business Source License 1.1 (BUSL-1.1)** — free for personal, internal research, and internal corporate ESG reporting. It converts to **Apache License 2.0** on July 25, 2030.

SustainableX retains the name "ai4sustainablex", the branding, and the SustainableX Template Library / Validation service (accessible via the SustainableX API).

See [LICENSE](LICENSE) for full terms and [COMMERCIAL.md](COMMERCIAL.md) for the free-vs-paid breakdown.

---

<p align="center">
  <strong>🌱 ai4sustainablex</strong><br>
  <em>Drafts from your documents. Every claim cited. Every gap flagged.</em><br>
  <a href="https://sustainablex.in">sustainablex.in</a> | <a href="mailto:info@sustainablex.in">info@sustainablex.in</a>
</p>
