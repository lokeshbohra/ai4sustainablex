#!/bin/bash
# ────────────────────────────────────────────────────────────────
# ai4sustainablex — One-Command Uninstaller (curl | bash)
# Removes the app, data workspace, and config created by install.sh
# https://github.com/lokeshbohra/ai4sustainablex
# ────────────────────────────────────────────────────────────────
set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🌱  ai4sustainablex  —  Uninstaller                  ║"
echo "║                                                              ║"
echo "║   This removes the app, data, and config from this machine.  ║"
echo "║   Your other files and Ollama models are NOT touched.        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ─── 1. Stop the backend server on port 8000 ──────────────────
echo "🛑 Stopping ai4sustainablex server (port 8000)..."
STOPPED=0
for PID in $(lsof -ti :8000 2>/dev/null || true); do
    if kill "$PID" 2>/dev/null; then
        STOPPED=1
    fi
done
if [ "$STOPPED" = "1" ]; then
    echo "   Server stopped."
else
    echo "   No server was running."
fi
echo ""

# ─── 2. Find the app install directory ─────────────────────────
INSTALL_DIR=""
RECEIPT="${HOME}/.ai4sustainablex/install_receipt"
if [ -f "${RECEIPT}" ]; then
    INSTALL_DIR="$(sed -n 's/^install_dir=//p' "${RECEIPT}" | head -1)"
fi
if [ -z "${INSTALL_DIR}" ] && [ -f "${HOME}/ai4sustainablex/main.py" ]; then
    INSTALL_DIR="${HOME}/ai4sustainablex"
fi

# ─── 3. Remove the app directory ───────────────────────────────
if [ -n "${INSTALL_DIR}" ] && [ -d "${INSTALL_DIR}" ]; then
    rm -rf "${INSTALL_DIR}"
    echo "✅ Removed app: ${INSTALL_DIR}"
else
    echo "ℹ️  No app folder found to remove."
fi
echo ""

# ─── 4. Remove data workspace and config ───────────────────────
for DIR in "${HOME}/ai4sustainablex_workspace" "${HOME}/.ai4sustainablex"; do
    if [ -d "${DIR}" ]; then
        rm -rf "${DIR}"
        echo "✅ Removed: ${DIR}"
    fi
done
echo ""

# ─── 5. Optionally remove the downloaded Ollama model ──────────
if command -v ollama >/dev/null 2>&1 && ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
    ANS="n"
    if [ -e /dev/tty ]; then
        echo -n "Also remove the downloaded model llama3.2:1b (~1.3 GB)? [y/N] "
        read -r -t 15 ANS </dev/tty || ANS="n"
    fi
    case "${ANS}" in
        y|Y|yes|Yes|YES)
            ollama rm llama3.2:1b >/dev/null 2>&1 && echo "✅ Removed model: llama3.2:1b" || echo "⚠️  Could not remove model (run 'ollama rm llama3.2:1b' manually)."
            ;;
        *)
            echo "ℹ️  Skipped model removal. Remove anytime with: ollama rm llama3.2:1b"
            ;;
    esac
fi
echo ""

echo "✅ ai4sustainablex has been removed."
echo "   Note: the Ollama runtime and any other models were NOT removed."
echo ""
