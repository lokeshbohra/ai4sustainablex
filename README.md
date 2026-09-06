# 🌱 ai4sustainablex

**Local-First AI Toolkit for ESG & Sustainability Reporting**

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Node.js Optional](https://img.shields.io/badge/node.js-18+-optional-orange.svg)](https://nodejs.org/)

> One command. Your documents. Private AI-powered ESG reports.
> All data stays on your machine. No cloud dependency.

---

## 📖 Table of Contents

- [What is ai4sustainablex?](#what-is-ai4sustainablex)
- [Features](#features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [LLM Providers](#llm-providers)
- [Report Templates](#report-templates)
- [Search Engines](#search-engines)
- [Data Connectors](#data-connectors)
- [Anti-Hallucination](#anti-hallucination)
- [Knowledge Graph](#knowledge-graph)
- [GUI (Optional)](#gui-optional)
- [System Requirements](#system-requirements)
- [Limitations](#limitations)
- [Capabilities](#capabilities)
- [FAQ](#faq)
- [Support](#support)
- [License](#license)

---

## What is ai4sustainablex?

**ai4sustainablex** is a zero-configuration, local-first desktop application for ESG and sustainability reporting. It gives you:

- A complete local AI assistant for ESG reporting — **no cloud required**
- **Hybrid RAG** (BM25 + Dense FAISS) search across your documents
- **13+ report templates** aligned with GRI, SBTi, CDP, IFRS S1/S2, CSRD, CSDDD, BRSR, and AFOLU/FLAG/REDD+
- **One-command install** (`curl | bash`) — inspired by Ollama, Claude Code, and OpenClaw
- **Multi-provider LLM** support (Ollama, OpenAI, Anthropic, DeepSeek, Gemini, Kimi K2)
- **Built-in anti-hallucination** verification via JavaScript engine
- **Knowledge graph** for entity relationships and cross-document connections

It's built for ESG practitioners who need to search, analyze, and generate sustainability reports from their documents — privately, securely, and without uploading sensitive data anywhere.

**Positioning**: Claude Code for ESG reporting. OpenClaw for sustainability. Ollama for compliance teams.

---

## Features

| Category | Capability |
|----------|-----------|
| 🔍 **Hybrid Search** | BM25 keyword + Dense FAISS semantic retrieval with weighted RRF ranking |
| 💬 **RAG Q&A** | Ask questions against your indexed documents with source citations |
| 📝 **13 Report Templates** | GRI, SBTi, CDP, IFRS S1/S2, CSRD, CSDDD, BRSR, AFOLU/FLAG, REDD+, Africa-Climate-Gender |
| 🧠 **6 LLM Providers** | Ollama (local), OpenAI, Anthropic Claude, DeepSeek, Google Gemini, Kimi K2 |
| 🛡️ **Anti-Hallucination** | JavaScript claims verification engine with confidence scoring |
| 🕸️ **Knowledge Graph** | Entity extraction, topic clustering, document-document relationships |
| 🔌 **Plugin Connectors** | SustainableX API, DuckDuckGo, Tavily, parallel search, MCP-style architecture |
| 📄 **Multi-Format Output** | Markdown, PDF (WeasyPrint), DOCX (python-docx) |
| 🖥️ **Desktop GUI** | Optional Electron-based graphical interface for non-CLI users |
| 🏠 **100% Local-First** | All processing, indexing, and inference on your machine (with Ollama) |
| ⚡ **One-Command Install** | `curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/install.sh | bash` |

---

## Quick Start

### Option A: One-Command Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/install.sh | bash
```

The installer auto-detects your OS, installs Ollama, pulls the default model (llama3.2:1b), sets up Python, and starts the backend server. Takes 3-5 minutes.

### Option B: Manual Install

```bash
# Clone the repository
git clone https://github.com/sustainablex/ai4sustainablex.git
cd ai4sustainablex

# Run the installer
chmod +x install.sh
./install.sh

# Or set up manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Your First 3 Commands

```bash
# 1. Interactive setup (accept ToS, choose folders, configure providers)
python cli.py setup

# 2. Index your ESG documents
python cli.py init ~/Documents/ESG_Reports

# 3. Ask a question
python cli.py ask "What are our Scope 1 emissions for 2024?"
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ai4sustainablex Desktop App                   │
│                                                                  │
│  ┌───────────┐  ┌───────────┐  ┌────────────┐  ┌─────────────┐ │
│  │  CLI      │  │  GUI      │  │  Setup     │  │  Plugin     │ │
│  │  (Click)  │  │  (Electron)│  │  Wizard    │  │  Manager    │ │
│  └─────┬─────┘  └─────┬─────┘  └─────┬──────┘  └──────┬──────┘ │
│        └──────────────┼──────────────┼────────────────┘        │
│                       ▼              ▼                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (port 8000)                  │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │   │
│  │  │ Hybrid RAG   │  │ Knowledge    │  │ Report Builder │ │   │
│  │  │ (BM25+FAISS) │  │ Graph        │  │ + Templates    │ │   │
│  │  └──────────────┘  └──────────────┘  └────────────────┘ │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LLM Providers: Ollama | OpenAI | Claude | DeepSeek |    │   │
│  │                 Gemini | Kimi K2                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    Local File System    │
              │  • Indexed Documents    │
              │  • Vector DB (FAISS)    │
              │  • Knowledge Graph      │
              │  • Generated Reports    │
              └─────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Install Script** | Bash + Python |
| **Backend API** | Python 3.10+ + FastAPI |
| **CLI Frontend** | Click + Rich (terminal) |
| **GUI Frontend** | Electron + HTML/CSS/JS |
| **Local LLM** | Ollama (llama3.2:1b default) |
| **Vector DB** | FAISS (local, CPU-optimized) |
| **Embeddings** | SentenceTransformers (all-MiniLM-L6-v2) |
| **RAG Framework** | Custom hybrid (BM25 + Dense RRF) |
| **Knowledge Graph** | NetworkX + custom entity extraction |
| **Anti-Hallucination** | Node.js custom claims verifier |
| **Document Formats** | PDF, DOCX, TXT, PPTX, XLSX |
| **Report Output** | Markdown, PDF (WeasyPrint), DOCX (python-docx) |

---

## Installation

### Supported Platforms

| Platform | Command |
|----------|---------|
| **macOS** | `curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/install.sh \| bash` |
| **Linux** | `curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/install.sh \| bash` |
| **Windows (WSL)** | `curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/install.sh \| bash` |
| **Windows (PowerShell)** | `irm https://sustainablex.in/install.ps1 \| iex` |

### Uninstall

Run this to completely remove ai4sustainablex (app, data, and config):

```bash
curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/uninstall.sh | bash
```

It stops the server, deletes the app, the data workspace (`~/ai4sustainablex_workspace`), and config (`~/.ai4sustainablex`), then asks before removing the downloaded Ollama model. Your other files and Ollama models are untouched.

### What the Installer Does

1. **Detects your OS** (macOS / Linux / Windows)
2. **Checks Python 3.10+** — installs if missing
3. **Installs Ollama** (local LLM runtime)
4. **Pulls default model** — `llama3.2:1b` (~1.3GB, runs on CPU)
5. **Creates Python virtual environment**
6. **Installs all dependencies** from `requirements.txt`
7. **Starts the backend server** on `http://localhost:8000`
8. **Prompts you** to run the interactive setup wizard

### API Keys (Optional)

Export these before running if you plan to use cloud providers:

```bash
export SUSTAINABLEX_API_KEY='sk-...'      # Premium ESG templates
export TAVILY_API_KEY='tvly-...'           # Enhanced web search
export OPENAI_API_KEY='sk-...'             # GPT-4o
export ANTHROPIC_API_KEY='sk-ant-...'      # Claude
export DEEPSEEK_API_KEY='sk-...'           # DeepSeek
export GEMINI_API_KEY='...'                 # Google Gemini
export KIMI_API_KEY='sk-...'              # Kimi K2
```

These are **NOT required**. ai4sustainablex works fully offline with Ollama as the default.

---

## Usage Guide

### CLI Commands Reference

```bash
# ─── Setup & Status ────────────────────────────────
python cli.py setup                    # Interactive first-time setup wizard
python cli.py status                   # Show system status and health
python cli.py ui                       # Open web interface (http://localhost:8000/docs)

# ─── Document Indexing ─────────────────────────────
python cli.py init ~/Documents/ESG     # Index a folder of ESG documents
python cli.py init                      # Use folder from config

# ─── Q&A / Chat ────────────────────────────────────
python cli.py ask "What are our Scope 1 emissions?"
python cli.py ask "Compare carbon footprint 2023 vs 2024" --search-type hybrid

# ─── Semantic Search ───────────────────────────────
python cli.py search "renewable energy targets"
python cli.py search "supply chain emissions" --web    # Include web search
python cli.py search "biodiversity" --search-type bm25  # Keyword-only search

# ─── Report Generation ─────────────────────────────
python cli.py report                                  # Default ESG report
python cli.py report -t ghg-emissions -c "Acme Corp" -p "FY2024"
python cli.py report -t sbcds-targets -c "Acme Corp" -p "FY2024" -f pdf
python cli.py report -t africa-climate-gender -q "Kenya and Tanzania"

# ─── Templates ─────────────────────────────────────
python cli.py templates               # List all templates
python cli.py templates --free        # Free templates only
python cli.py templates --premium     # Premium templates
python cli.py templates -s GRI        # Search by keyword
python cli.py templates -c SBTi       # Filter by category

# ─── LLM Providers ─────────────────────────────────
python cli.py providers list          # List all providers
python cli.py providers models        # List Ollama models
python cli.py providers models -p openai  # List OpenAI models
python cli.py providers switch openai --model gpt-4o

# ─── Knowledge Graph ───────────────────────────────
python cli.py graph stats             # Graph statistics
python cli.py graph entity "Scope 1"  # Query an entity

# ─── Connectors ────────────────────────────────────
python cli.py connectors sx           # SustainableX API status
python cli.py connectors search       # Search engine status
```

### API Endpoints

All commands above use the REST API. See `http://localhost:8000/docs` for full Swagger documentation.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/index` | Index a folder of ESG documents |
| `POST` | `/search` | Hybrid BM25 + Dense search |
| `POST` | `/chat` | RAG-enhanced Q&A |
| `POST` | `/generate_report` | Generate ESG report |
| `GET`  | `/templates` | List available templates |
| `POST` | `/providers/switch` | Switch LLM provider |
| `GET`  | `/graph/entity/{entity}` | Query knowledge graph |
| `GET`  | `/status` | Full system status |
| `GET`  | `/health` | Health check |

---

## LLM Providers

ai4sustainablex supports **6 LLM providers** — one local, five cloud-based:

| Provider | Type | Default Model | API Key | Notes |
|----------|------|---------------|---------|-------|
| **Ollama** | Local | `llama3.2:1b` | None | Default. Fully offline. Smallest. |
| **OpenAI** | Cloud | `gpt-4o-mini` | Required | Highest quality |
| **Anthropic** | Cloud | `claude-3-5-sonnet` | Required | Best for long reports |
| **DeepSeek** | Cloud | `deepseek-chat` | Required | Cost-effective |
| **Gemini** | Cloud | `gemini-2.0-flash` | Required | Good for structured output |
| **Kimi K2** | Cloud | `moonshot-v1-8k` | Required | Large context window |

**Switching providers**:
```bash
python cli.py providers switch openai --model gpt-4o
python cli.py providers switch anthropic
python cli.py providers switch ollama --model llama3.2:3b
```

**Changing the default Ollama model**:
```bash
# Pull a different model
ollama pull llama3.2:3b      # 3B parameters (~2GB)
ollama pull mistral           # 7B (~4.1GB)
ollama pull deepseek-r1:7b    # With reasoning
ollama pull gemma3:12b        # Larger model

# Then switch in ai4sustainablex
python cli.py providers switch ollama -m llama3.2:3b
```

---

## Report Templates

### Free Templates (5)

| Template ID | Name | Framework | Sections |
|-------------|------|-----------|----------|
| `esg-report-basic` | Basic ESG Report | GRI | 9 sections |
| `ghg-emissions` | GHG Emissions Analysis | GRI | 10 sections |
| `carbon-footprint` | Carbon Footprint Analysis | CDP | 10 sections |
| `sustainability-brief` | Sustainability Brief | Multi | 8 sections |
| `compliance-checklist` | ESG Compliance Checklist | Multi | 8 sections |

### Premium Templates (8 — require SustainableX API key)

| Template ID | Name | Framework |
|-------------|------|-----------|
| `gri-full-report` | GRI Standards Full Report | GRI 2021 |
| `sbcds-targets` | SBTi Target Setting & Validation | SBTi |
| `cdp-disclosure` | CDP Climate Change Disclosure | CDP |
| `ifrs-s1-s2` | IFRS S1 & S2 Sustainability Disclosures | ISSB |
| `csrd-esrs` | CSRD / ESRS Compliance Report | ESRS |
| `csddd-due-diligence` | CSDDD Due Diligence Report | CSDDD |
| `afolu-flag-redd` | AFOLU, FLAG & REDD+ Project Report | VCS/CCB |
| `africa-climate-gender` | Africa Climate, Gender & Livelihoods Nexus | Multi |
| `brsr-report` | BRSR Comprehensive Report (India) | BRSR |

---

## Search Engines

| Engine | Type | API Key | Rate Limit | Notes |
|--------|------|---------|------------|-------|
| **DuckDuckGo** | Web Search | None | Moderate | Default. Always enabled. |
| **Tavily** | Semantic Search | `TAVILY_API_KEY` | Per plan | Optimized for research |

Search engines can be queried in parallel (both engines simultaneously) to cross-reference results.

**Search modes:**
- `hybrid` — BM25 + Dense combined (default, best accuracy)
- `bm25` — Keyword-only (fast, exact matches)
- `dense` — Semantic-only (conceptual matching)

---

## Data Connectors

ai4sustainablex uses an **MCP-style (Model-Connector-Plugin)** architecture for extensibility:

```
connectors/
├── base.py              # Abstract plugin class
├── sustainablex_api.py  # Template library (API key)
├── sustainablex_data.py # ESG data & frameworks
└── search_engines.py    # DuckDuckGo + Tavily
```

All connectors inherit from `BaseConnector` and implement: `authenticate()`, `fetch()`, `search()`, `get_templates()`, `health_check()`, and `validate_key()`.

**Adding a new connector:**
1. Create a class inheriting from `BaseConnector`
2. Implement the required methods
3. Register in `connectors/__init__.py`

---

## Anti-Hallucination

ai4sustainablex includes a **JavaScript-based claims verification engine** (`anti_hallucination.js`) that:

- **Extracts claims** from LLM-generated responses
- **Matches each claim** against source document chunks
- **Scores confidence** using exact phrase matching and term overlap
- **Flags unsupported claims** with severity warnings
- **Generates citations** for supported claims
- **Produces a grounding score** (0-100) for the overall report

**How it works:**
```
LLM Response → Extract claims → Match against sources
             → Score each claim (0-1 confidence)
             → Verdict: highly_reliable / mostly_reliable / moderate / low_confidence / unreliable
             → Flag unsupported claims with suggested actions
```

**Run manually (optional):**
```bash
node anti_hallucination.js --answer "The company reduced emissions by 15%" \
    --sources "Source 1 text with 15% figure|Source 2 text about emissions"
```

---

## Knowledge Graph

The knowledge graph provides entity-level context for reports:

- **Entity extraction** — Identifies ESG entities (GHG, CO2, GRI, SBTi, CDP, frameworks, metrics)
- **Topic clustering** — Groups related chunks into topics
- **Document hierarchy** — Maps folder structures and page-level references
- **Cross-document connections** — Finds documents sharing entities and concepts

**Use in reports**: Reports automatically pull related entities and connected documents to enrich context.

---

## GUI (Optional)

For users who prefer a graphical interface:

```bash
cd gui
npm install
npm start
```

The Electron shell spawns the Python backend and loads the web interface at `http://localhost:8000`. It provides:

- Visual search bar for asking questions
- One-click access to API docs
- System status indicator
- Links to templates, search, and report endpoints

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | macOS 13+ / Ubuntu 20.04+ / Windows 10+ | Latest |
| **RAM** | 8 GB | 16 GB+ |
| **Disk** | 4 GB free | 10 GB+ (multiple models) |
| **Python** | 3.10+ | 3.11+ |
| **Ollama** | Latest | Latest |
| **Node.js** | 18+ (optional) | 20+ (optional) |

**Default model**: `llama3.2:1b` uses ~1.3GB disk and runs comfortably on 8GB RAM with CPU-only inference.

---

## Limitations

### Technical Limitations

- **Only folders you specify** are indexed — no recursive system scanning
- **FAISS is CPU-only** by default (GPU version requires `faiss-gpu`)
- **Large document sets** (1000+ files) may need more RAM for indexing
- **Embedding model** (MiniLM-L6-v2, 384 dimensions) trades some accuracy for speed and local execution
- **PDF extraction** depends on embedded text — scanned-image PDFs need OCR (not included)

### Functional Limitations

- **Reports are AI-generated drafts** — always review by a professional
- **Template alignment** — templates follow framework structures but may not reflect the very latest amendments
- **No real-time collaboration** — single-user local tool
- **No regulatory guarantee** — generated reports are not assurance-ready without human review
- **Premium templates** — require a SustainableX API key from https://sustainablex.in
- **Africa Climate template** — provides structural analysis only; ground-truth data must be supplied by user

---

## Capabilities

### What ai4sustainablex CAN do

✅ Index and search across PDF, DOCX, TXT, PPTX, XLSX files
✅ Perform hybrid keyword + semantic search with source citations
✅ Answer questions grounded in your documents (RAG)
✅ Generate 13 types of ESG/Sustainability reports
✅ Run entirely offline with Ollama (no internet needed after model download)
✅ Switch between 6 LLM providers at runtime
✅ Verify AI-generated claims against source documents
✅ Build knowledge graphs from your documents
✅ Supplement reports with web research (DuckDuckGo/Tavily)
✅ Export reports as Markdown, PDF, or DOCX
✅ Extend via MCP-style connector plugins

### What ai4sustainablex CANNOT do

❌ Replace a professional ESG consultant
❌ Guarantee regulatory compliance
❌ Access files outside the explicitly specified folder
❌ Upload your data anywhere (by design)
❌ OCR scanned-image PDFs (requires separate OCR tool)
❌ Collaborate in real-time with other users
❌ Connect to live ERP/accounting systems (plugin needed)

---

## FAQ

**Q: Is my data safe?**
A: Yes. All processing is local. No documents, queries, or indexed data ever leave your machine unless you explicitly configure a cloud-based LLM provider. Read our full [Disclaimer](DISCLAIMER.md).

**Q: Do I need an internet connection?**
A: Internet is required only for installation and model download. After that, Ollama-based usage works fully offline. Cloud providers (OpenAI, Claude, etc.) require internet.

**Q: What's the smallest model I can use?**
A: `llama3.2:1b` (~1.3GB). It's fast, runs on CPU, and handles ESG reporting tasks well. Pull it with: `ollama pull llama3.2:1b`

**Q: Can I use my own GGUF model files?**
A: Yes. Create an Ollama Modelfile pointing to your GGUF file and run `ollama create my-model -f Modelfile`. Then switch: `python cli.py providers switch ollama -m my-model`

**Q: How do I update ai4sustainablex?**
A: Re-run the installer: `curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/install.sh | bash`. Or pull the latest from GitHub and run `pip install -r requirements.txt --upgrade`.

**Q: How do I get the premium templates?**
A: Get an API key at https://sustainablex.in and configure it during setup or export `SUSTAINABLEX_API_KEY`.

**Q: Does it support non-English documents?**
A: The embedding model (MiniLM) supports 50+ languages. The LLM's language support depends on the model — most modern models handle multilingual input.

**Q: Can I run it on a server for my team?**
A: The FastAPI backend can be deployed behind a reverse proxy with authentication. Note that this is a single-user tool by design — concurrent users would need separate indexes.

---

## Support

- **🌐 Website**: [https://sustainablex.in](https://sustainablex.in)
- **📧 Email**: [info@sustainablex.in](mailto:info@sustainablex.in)
- **🐛 Issues**: [GitHub Issues](https://github.com/sustainablex/ai4sustainablex/issues)
- **💬 Community**: [GitHub Discussions](https://github.com/sustainablex/ai4sustainablex/discussions)
- **📖 API Docs**: `http://localhost:8000/docs` (when running)

---

## License

ai4sustainablex is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

SustainableX retains rights to the name "ai4sustainablex", the branding, and the premium template library accessible via the SustainableX API.

See [LICENSE](LICENSE) for the full text.

---

<p align="center">
  <strong>🌱 ai4sustainablex</strong><br>
  <em>Local-First. Private. Open Source.</em><br>
  <a href="https://sustainablex.in">sustainablex.in</a> | <a href="mailto:info@sustainablex.in">info@sustainablex.in</a>
</p>