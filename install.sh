#!/bin/bash
# ────────────────────────────────────────────────────────────────
# ai4sustainablex — One-Command Installer (curl | bash)
# ESG drafts from your documents — cited, gap-flagged, local
# https://sustainablex.in  |  info@sustainablex.in
# ────────────────────────────────────────────────────────────────
set -e

# ─── Branding ──────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🌱  ai4sustainablex  —  Installer                    ║"
echo "║                                                              ║"
echo "║   ESG drafts from your documents — cited, gap-flagged, local  ║"
echo "║   https://sustainablex.in                                    ║"
echo "║   info@sustainablex.in                                       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ─── OS Detection ──────────────────────────────────────────────
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE="Linux";;
    Darwin*)    MACHINE="Mac";;
    CYGWIN*|MINGW*|MSYS*) MACHINE="Windows";;
    *)          MACHINE="UNKNOWN";;
esac

echo "🖥️  Detected OS: ${MACHINE}"
echo "──────────────────────────────────────────────────────────────"
echo ""

# ─── Python Check ──────────────────────────────────────────────
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON=$(command -v python3)
    PYTHON_VERSION=$($PYTHON --version 2>&1)
    echo "✅ Found: ${PYTHON_VERSION} (${PYTHON})"
elif command -v python &> /dev/null; then
    PYTHON=$(command -v python)
    PYTHON_VERSION=$($PYTHON --version 2>&1)
    echo "✅ Found: ${PYTHON_VERSION} (${PYTHON})"
else
    echo "❌ Python 3 not found. Please install Python 3.10+:"
    echo "   macOS: brew install python@3.11"
    echo "   Linux: sudo apt install python3 python3-pip python3-venv"
    echo "   Windows: https://www.python.org/downloads/"
    exit 1
fi
echo ""

# ─── Ollama Check & Install ────────────────────────────────────
echo "📦 Checking Ollama (local LLM runtime)..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama already installed."
    OLLAMA_VERSION=$(ollama --version 2>&1 || echo "unknown version")
    echo "   ${OLLAMA_VERSION}"
else
    echo "📥 Installing Ollama..."
    if [ "$MACHINE" == "Mac" ]; then
        curl -fsSL https://ollama.com/install.sh | sh
    elif [ "$MACHINE" == "Linux" ]; then
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "⚠️  Windows detected. Please install Ollama from:"
        echo "   https://ollama.com/download/windows"
        echo "   Then re-run this installer."
    fi
    
    # Verify installation
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama installed successfully."
    else
        echo "⚠️  Ollama installation may have failed. Continuing anyway..."
    fi
fi
echo ""

# ─── Model Pull (Background) ───────────────────────────────────
echo "🧠 Pulling default model: llama3.2:1b (~1.3GB)..."
echo "   (This runs in the background — you can start using ai4sustainablex immediately)"
echo "   To use a different model, run: ollama pull <model-name>"
echo "   Examples: ollama pull llama3.2:3b"
echo "             ollama pull mistral"
echo "             ollama pull deepseek-r1:7b"
echo ""

if command -v ollama &> /dev/null; then
    # Pull in background so install doesn't block
    ollama pull llama3.2:1b &
    OLLAMA_PID=$!
    echo "   📥 Pulling in background (PID: $OLLAMA_PID)."
    echo "   Check progress: ollama list"
else
    echo "   ⚠️  Ollama not available. Skip model pull."
    echo "   Install Ollama and run: ollama pull llama3.2:1b"
fi
echo ""

# ─── Node.js Check (for anti-hallucination engine) ─────────────
echo "📦 Checking Node.js (for anti-hallucination verification)..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    echo "✅ Node.js found: ${NODE_VERSION}"
else
    echo "ℹ️  Node.js not found. Anti-hallucination verification will use fallback."
    echo "   Install Node.js from https://nodejs.org for full verification."
fi
echo ""

# ─── Ensure Application Code Is Present ────────────────────────
# When installed via `curl ... | bash`, only THIS script is streamed.
# If main.py is missing, we are not inside a repo checkout — download
# the full application from GitHub so the one-command install works.
REPO_URL="https://github.com/lokeshbohra/ai4sustainablex"

if [ ! -f "main.py" ]; then
    echo "📦 ai4sustainablex code not found in the current directory."
    echo "   Downloading from GitHub: ${REPO_URL}"

    # If the current directory isn't empty, install into a dedicated app dir.
    if [ -n "$(ls -A . 2>/dev/null)" ]; then
        APP_DIR="${AI4SX_INSTALL_DIR:-$HOME/ai4sustainablex}"
        echo ""
        echo "   Current directory is not empty — installing into: ${APP_DIR}"
        mkdir -p "${APP_DIR}"
        cd "${APP_DIR}"
    fi

    if [ ! -f "main.py" ]; then
        echo ""
        if command -v git >/dev/null 2>&1; then
            echo "   Cloning repository with git..."
            git clone --depth 1 "${REPO_URL}.git" .
        else
            echo "   git not found — downloading source tarball instead..."
            curl -fsSL "${REPO_URL}/archive/refs/heads/main.tar.gz" | tar -xz --strip-components=1
        fi
    fi

    if [ -f "main.py" ]; then
        echo "✅ Application code downloaded. Resuming install..."
    else
        echo ""
        echo "❌ Could not download application code from: ${REPO_URL}"
        exit 1
    fi
    echo ""
fi

# ─── Python Virtual Environment ────────────────────────────────
echo "🐍 Setting up Python virtual environment..."
cd "$(dirname "$0")" 2>/dev/null || cd "$(pwd)"

if [ -d "venv" ]; then
    echo "   Virtual environment already exists. Updating..."
else
    $PYTHON -m venv venv
    echo "✅ Virtual environment created."
fi

# Activate
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "⚠️  Cannot activate virtual environment."
fi
echo ""

# ─── Install Python Dependencies ───────────────────────────────
echo "📚 Installing Python dependencies..."
echo "   This may take 3-5 minutes on first run..."
pip install --upgrade pip --quiet 2>/dev/null

# Install core dependencies first
echo "   Installing core packages..."
pip install --quiet \
    fastapi uvicorn[standard] click rich typer pydantic \
    requests python-multipart python-dotenv httpx 2>/dev/null || true

# Install RAG packages
echo "   Installing RAG packages..."
pip install --quiet \
    langchain langchain-community faiss-cpu sentence-transformers \
    rank-bm25 pypdf python-docx tqdm numpy 2>/dev/null || true

# Install optional packages
echo "   Installing optional packages (errors are OK)..."
pip install --quiet \
    duckduckgo-search beautifulsoup4 networkx \
    openai anthropic google-generativeai 2>/dev/null || true

echo "✅ Dependencies installed."
echo ""

# ─── Create Storage Directories ────────────────────────────────
echo "📁 Creating storage directories..."
mkdir -p storage/vector_db storage/knowledge_graph storage/reports storage/templates_cache

# Create default workspace
WORKSPACE_DIR="${HOME}/ai4sustainablex_workspace"
mkdir -p "${WORKSPACE_DIR}/companies" "${WORKSPACE_DIR}/output" "${WORKSPACE_DIR}/vector_db" "${WORKSPACE_DIR}/stats"
echo "✅ Storage directories ready."
echo "   Workspace: ${WORKSPACE_DIR}"
echo ""

# ─── Set Executable Permissions ────────────────────────────────
chmod +x cli.py 2>/dev/null || true
chmod +x anti_hallucination.js 2>/dev/null || true

# ─── API Key Notice ────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🔑 Optional API Keys (not required for basic usage)        ║"
echo "║                                                              ║"
echo "║  • SustainableX API Key — premium ESG templates             ║"
echo "║    Get one at: https://sustainablex.in                      ║"
echo "║    Export: export SUSTAINABLEX_API_KEY='your-key'           ║"
echo "║                                                              ║"
echo "║  • Tavily Search API — enhanced web research                ║"
echo "║    Get one at: https://tavily.com                           ║"
echo "║    Export: export TAVILY_API_KEY='your-key'                 ║"
echo "║                                                              ║"
echo "║  • OpenAI / Anthropic / DeepSeek / Gemini / Kimi            ║"
echo "║    Export corresponding API key or configure in setup       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ─── Start Backend Server ──────────────────────────────────────
echo "🚀 Starting ai4sustainablex backend server..."
if [ -f "venv/bin/python" ]; then
    VENV_PYTHON="venv/bin/python"
elif [ -f "venv/Scripts/python" ]; then
    VENV_PYTHON="venv/Scripts/python"
else
    VENV_PYTHON="$PYTHON"
fi

nohup $VENV_PYTHON main.py > esg.log 2>&1 &
SERVER_PID=$!
echo "   Server PID: $SERVER_PID"
echo "   Log: esg.log"

# Wait briefly to confirm startup
sleep 3
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Backend server started successfully."
else
    echo "⚠️  Server may not have started. Check esg.log for details."
fi
echo ""

# ─── Installation Complete ─────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        ✅  ai4sustainablex Installation Complete!           ║"
echo "║                                                              ║"
echo "║   🚀 Quick Start:                                           ║"
echo "║                                                              ║"
echo "║   # Activate environment (if not already)                    ║"
echo "║   source venv/bin/activate                                  ║"
echo "║                                                              ║"
echo "║   # Run interactive setup:                                  ║"
echo "║   python cli.py setup                                       ║"
echo "║                                                              ║"
echo "║   # Or start using immediately:                             ║"
echo "║   python cli.py init ~/Documents                            ║"
echo "║   python cli.py ask \"What are our carbon emissions?\"       ║"
echo "║   python cli.py report -t esg-report-basic                  ║"
echo "║                                                              ║"
echo "║   🌐 API Docs: http://localhost:8000/docs                   ║"
echo "║   🌐 Website:  https://sustainablex.in                      ║"
echo "║   📧 Support:  info@sustainablex.in                         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Wait for Ollama pull if it was started
if [ -n "$OLLAMA_PID" ] && kill -0 $OLLAMA_PID 2>/dev/null; then
    echo "📥 Ollama model pull is still running in background (PID: $OLLAMA_PID)."
    echo "   You can start using ai4sustainablex now — the model will be ready soon."
    echo "   Check: ollama list"
fi

# ─── Record Install Location (for uninstall.sh) ────────────────
mkdir -p "${HOME}/.ai4sustainablex"
echo "install_dir=$(pwd)" > "${HOME}/.ai4sustainablex/install_receipt"
echo "installed_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${HOME}/.ai4sustainablex/install_receipt"
echo "✅ Install receipt saved to ~/.ai4sustainablex/install_receipt"
echo "   To remove later: curl -fsSL https://raw.githubusercontent.com/lokeshbohra/ai4sustainablex/main/uninstall.sh | bash"
echo ""

echo ""