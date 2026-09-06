"""
ai4sustainablex — Interactive Setup & Onboarding Wizard
First-time setup wizard for ai4sustainablex.
Handles ToS acceptance, folder selection, LLM provider configuration,
API key entry, search engine setup, and initial document indexing.
"""

import os
import json
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

# Configuration file path
CONFIG_DIR = os.path.expanduser("~/.ai4sustainablex")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


class SetupWizard:
    """
    Interactive CLI setup wizard for ai4sustainablex.

    Steps:
    1. Welcome & Branding
    2. Terms of Service & Disclaimer
    3. Document Folder Selection
    4. LLM Provider Configuration
    5. Search Engine Setup
    6. SustainableX API Key (optional)
    7. Template Library Access
    8. Initial Document Indexing
    9. Save Configuration
    """

    BRAND_HEADER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🌱  ai4sustainablex  —  Setup & Onboarding           ║
║                                                              ║
║   ESG drafts from your documents — cited, gap-flagged, local  ║
║   https://sustainablex.in                                    ║
║   info@sustainablex.in                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

    TOS_TEXT = """
TERMS OF SERVICE & DISCLAIMER
─────────────────────────────

ai4sustainablex ("the Software") is provided by SustainableX 
(https://sustainablex.in, info@sustainablex.in) under the 
following terms:

1. ACCEPTANCE OF TERMS
   By using ai4sustainablex, you agree to these Terms of Service.
   If you do not agree, do not use the Software.

2. DESCRIPTION OF SERVICE
   ai4sustainablex is a local-first AI toolkit for ESG and 
   sustainability reporting. It indexes documents, performs 
   semantic search, generates reports, and connects to LLMs 
   and data APIs.

3. LOCAL PROCESSING
   All document processing, vector indexing, and LLM inference 
   (when using Ollama) happens locally on your machine. Data 
   is NOT uploaded to any cloud service unless you explicitly 
   configure cloud-based providers (OpenAI, Anthropic, etc.).

4. NO LIABILITY — USER FILES & FOLDER STRUCTURES
   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY 
   KIND. SustainableX and its contributors SHALL NOT BE LIABLE 
   for any:
   - Loss, corruption, or modification of user files
   - Damage to folder structures or file systems
   - Data loss resulting from indexing or processing
   - Inaccuracies in generated reports or AI outputs
   - Decisions made based on AI-generated content

5. ACCESS RESTRICTIONS
   The Software only accesses folders explicitly specified by 
   you during setup. It will not scan, read, or index files 
   outside the designated directory.

6. THIRD-PARTY SERVICES
   When using cloud-based LLM providers (OpenAI, Anthropic, 
   DeepSeek, Gemini, Kimi), your queries are transmitted to 
   their respective APIs. Review their privacy policies.

7. API KEYS
   API keys are stored locally in ~/.ai4sustainablex/config.json 
   and are never transmitted except to authenticate with the 
   respective service endpoints.

8. REPORT ACCURACY
   Generated reports combine retrieved documents with AI 
   generation. ALL reports should be reviewed by a qualified 
   professional before use. ai4sustainablex is an assistive 
   tool, NOT a substitute for professional ESG consulting.

9. INTELLECTUAL PROPERTY
   ai4sustainablex is licensed under [BUSL-1.1]. SustainableX 
   retains rights to the name, branding, and template library.

10. GOVERNING LAW
    These terms are governed by the laws of India. Disputes 
    shall be subject to the jurisdiction of courts in Mumbai.

By proceeding, you acknowledge that you have read, understood, 
and agree to these Terms of Service.
"""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self._load_existing_config()

    def run(self) -> Dict[str, Any]:
        """
        Run the full setup wizard interactively.

        Returns:
            Complete configuration dictionary
        """
        print(self.BRAND_HEADER)
        print("Welcome to ai4sustainablex! Let's get you set up.\n")

        # Step 1: ToS
        if not self._accept_tos():
            print("\n❌ Setup cancelled. You must accept the Terms of Service to continue.")
            sys.exit(1)

        # Step 2: Document Folder
        self._configure_document_folder()

        # Step 3: LLM Provider
        self._configure_llm_provider()

        # Step 4: Ollama Model (if Ollama selected)
        if self.config.get("llm_provider") == "ollama":
            self._configure_ollama_model()

        # Step 5: Search Engines
        self._configure_search_engines()

        # Step 6: SustainableX API
        self._configure_sustainablex_api()

        # Step 7: Template Library
        self._show_template_info()

        # Step 8: Initial Indexing
        self._offer_initial_indexing()

        # Step 9: Save
        self._save_config()

        # Done
        self._print_setup_complete()

        return self.config

    def _accept_tos(self) -> bool:
        """Display ToS and get user acceptance."""
        print(self.TOS_TEXT)
        print()
        response = input("Do you accept these Terms of Service? [yes/no]: ").strip().lower()
        if response in ("yes", "y"):
            self.config["tos_accepted"] = True
            self.config["tos_accepted_at"] = str(__import__("datetime").datetime.now())
            print("✅ Terms accepted.\n")
            return True
        return False

    def _configure_document_folder(self) -> None:
        """Get the document folder path from the user."""
        print("─" * 55)
        print("📁 Step 1: Document Folder")
        print("   Specify the folder containing your ESG reports and documents.")
        print("   Supported formats: PDF, DOCX, TXT, PPTX, XLSX\n")

        default_folder = os.path.expanduser("~/Documents")
        folder = input(f"Document folder path [{default_folder}]: ").strip()
        if not folder:
            folder = default_folder

        folder = os.path.expanduser(folder)
        if not os.path.exists(folder):
            print(f"⚠️  Folder '{folder}' does not exist. Creating it...")
            os.makedirs(folder, exist_ok=True)

        self.config["document_folder"] = folder
        print(f"✅ Document folder: {folder}\n")

    def _configure_llm_provider(self) -> None:
        """Select and configure the LLM provider."""
        print("─" * 55)
        print("🧠 Step 2: LLM Provider Selection")
        print("   Choose your preferred AI model provider:\n")
        providers = {
            "1": {"name": "ollama", "label": "Ollama (Local, Free, Private)"},
            "2": {"name": "openai", "label": "OpenAI GPT-4o (requires API key)"},
            "3": {"name": "anthropic", "label": "Anthropic Claude (requires API key)"},
            "4": {"name": "deepseek", "label": "DeepSeek (requires API key)"},
            "5": {"name": "gemini", "label": "Google Gemini (requires API key)"},
            "6": {"name": "kimi", "label": "Kimi / Moonshot (requires API key)"},
            "7": {"name": "grok", "label": "xAI Grok (requires API key)"},
            "8": {"name": "groq", "label": "Groq — Ultra-fast inference (requires API key)"},
            "9": {"name": "fugu", "label": "Sakana Fugu — Japanese optimized (requires API key)"},
            "10": {"name": "openrouter", "label": "OpenRouter — 200+ models (requires API key)"},
            "11": {"name": "glm", "label": "GLM / Zhipu AI (requires API key)"},
            "12": {"name": "qwen", "label": "Qwen / Alibaba (requires API key)"},
        }

        for key, provider in providers.items():
            print(f"   {key}. {provider['label']}")

        print()
        choice = input("Select provider [1]: ").strip() or "1"
        provider_key = providers.get(choice, providers["1"])

        self.config["llm_provider"] = provider_key["name"]
        print(f"✅ Selected: {provider_key['label']}")

        # API Key for cloud providers
        if provider_key["name"] != "ollama":
            env_vars = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "gemini": "GEMINI_API_KEY",
                "kimi": "KIMI_API_KEY",
            }
            env_var = env_vars[provider_key["name"]]
            existing_key = os.getenv(env_var, "")

            if existing_key:
                print(f"   Found {env_var} in environment.")
                use_existing = input(f"   Use existing {env_var}? [Y/n]: ").strip().lower()
                if use_existing in ("n", "no"):
                    existing_key = ""

            if not existing_key:
                api_key = input(f"   Enter {env_var}: ").strip()
                if api_key:
                    self.config[f"{provider_key['name']}_api_key"] = api_key
                    print(f"   ✅ API key configured for {provider_key['name']}")
                else:
                    print(f"   ⚠️  No API key provided. {provider_key['name']} will use default models only.")
            else:
                self.config[f"{provider_key['name']}_api_key"] = existing_key

            # Optional custom base URL
            base_url = input(f"   Custom base URL [default]: ").strip()
            if base_url:
                self.config[f"{provider_key['name']}_base_url"] = base_url

        print()

    def _configure_ollama_model(self) -> None:
        """Help user configure Ollama model."""
        print("─" * 55)
        print("📥 Step 2b: Ollama Model Configuration")
        print("   ai4sustainablex defaults to llama3.2:1b (smallest, fastest).")
        print("   You can change this now or later with:")
        print("   python cli.py providers models")
        print()
        print("   To pull a different model, run:")
        print("   ollama pull <model-name>")
        print("   Example: ollama pull llama3.2:3b")
        print("   Example: ollama pull mistral")
        print("   Example: ollama pull deepseek-r1:7b")
        print()

        model = input(f"Ollama model [llama3.2:1b]: ").strip()
        if model:
            self.config["ollama_model"] = model
        else:
            self.config["ollama_model"] = "llama3.2:1b"

        # Attempt to check if model exists, offer to pull
        print(f"\n   Checking for model '{self.config['ollama_model']}'...")
        try:
            import subprocess
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
            model_names = []
            for line in result.stdout.split("\n")[1:]:
                parts = line.split()
                if parts:
                    model_names.append(parts[0])

            exact_model = self.config["ollama_model"]
            model_base = exact_model.split(":")[0]

            if exact_model in model_names:
                print(f"   ✅ Model '{exact_model}' is already available.")
            elif model_base in result.stdout:
                print(f"   ✅ Model '{model_base}' (or variant) is already available.")
            else:
                print(f"   📥 Model '{exact_model}' not found locally.")
                pull = input(f"   Pull it now? (~2GB download) [Y/n]: ").strip().lower()
                if pull not in ("n", "no"):
                    print(f"   📥 Pulling {exact_model}... This may take a few minutes.")
                    subprocess.run(["ollama", "pull", exact_model])
                    print(f"   ✅ Model '{exact_model}' pulled successfully.")
        except FileNotFoundError:
            print("   ⚠️  Ollama not installed. Run: curl -fsSL https://ollama.com/install.sh | bash")
        except Exception:
            print("   ⚠️  Could not check Ollama models. Proceeding...")

        print()

    def _configure_search_engines(self) -> None:
        """Configure web search engines."""
        print("─" * 55)
        print("🔍 Step 3: Search Engine Configuration")
        print("   ai4sustainablex supports multiple search engines:")
        print()
        print("   • DuckDuckGo — Free, no API key required, rate-limited")
        print("   • Tavily — Optimized for research, requires API key")
        print()

        # DuckDuckGo is always enabled by default
        self.config["search_engines"] = ["duckduckgo"]

        enable_tavily = input("Configure Tavily API key? [y/N]: ").strip().lower()
        if enable_tavily in ("y", "yes"):
            tavily_key = os.getenv("TAVILY_API_KEY", "")
            if tavily_key:
                print(f"   Found TAVILY_API_KEY in environment.")
                use_env = input(f"   Use existing key? [Y/n]: ").strip().lower()
                if use_env in ("n", "no"):
                    tavily_key = ""

            if not tavily_key:
                tavily_key = input("   Enter TAVILY_API_KEY: ").strip()

            if tavily_key:
                self.config["tavily_api_key"] = tavily_key
                self.config["search_engines"].append("tavily")
                print("   ✅ Tavily search enabled.")

        print(f"   Active search engines: {', '.join(self.config['search_engines'])}")
        print()

    def _configure_sustainablex_api(self) -> None:
        """Configure SustainableX API for premium templates."""
        print("─" * 55)
        print("🔌 Step 4: SustainableX API (Optional)")
        print("   SustainableX provides premium ESG report templates:")
        print("   GRI, SBTi, CDP, IFRS S1/S2, CSRD, CSDDD, BRSR, AFOLU/FLAG")
        print("   and Africa Climate-Gender-Livelihoods templates.")
        print("   Get your API key at https://sustainablex.in")
        print()

        sx_key = os.getenv("SUSTAINABLEX_API_KEY", "")
        if sx_key:
            print("   Found SUSTAINABLEX_API_KEY in environment.")
            use_env = input("   Use existing key? [Y/n]: ").strip().lower()
            if use_env in ("n", "no"):
                sx_key = ""

        if not sx_key:
            sx_key = input("   Enter SUSTAINABLEX_API_KEY [skip]: ").strip()

        if sx_key:
            self.config["sustainablex_api_key"] = sx_key
            print("   ✅ SustainableX API configured.")
            print("   Premium templates will be available after authentication.")
        else:
            print("   ℹ️  Skipping — free templates (5) will be available.")

        print()

    def _show_template_info(self) -> None:
        """Show available template categories."""
        print("─" * 55)
        print("📋 Step 5: Template Library Overview")
        print()
        print("   FREE Templates (always available):")
        print("   • Basic ESG Report")
        print("   • GHG Emissions Analysis")
        print("   • Carbon Footprint Analysis")
        print("   • Sustainability Brief")
        print("   • ESG Compliance Checklist")
        print()
        print("   PREMIUM Templates (requires SustainableX API key):")
        print("   • GRI Standards Full Report")
        print("   • SBTi Target Setting & Validation")
        print("   • CDP Climate Change Disclosure")
        print("   • IFRS S1 & S2 Disclosures")
        print("   • CSRD / ESRS Compliance Report")
        print("   • CSDDD Due Diligence Report")
        print("   • AFOLU, FLAG & REDD+ Project Report")
        print("   • Africa Climate, Gender & Livelihoods Nexus")
        print("   • BRSR Comprehensive Report (India)")
        print()

    def _offer_initial_indexing(self) -> None:
        """Offer to index the document folder now."""
        print("─" * 55)
        print("📑 Step 6: Initial Document Indexing")
        print(f"   Your document folder: {self.config.get('document_folder', '~/Documents')}")
        print()

        do_index = input("Index documents now? (required before searching) [Y/n]: ").strip().lower()
        if do_index in ("n", "no"):
            print("   ℹ️  Skipping. Run 'python cli.py init <folder>' later.")
        else:
            print(f"   📁 Indexing {self.config['document_folder']}...")
            try:
                from rag_engine import HybridRAGEngine
                rag = HybridRAGEngine(storage_path="./storage/vector_db")
                result = rag.index_folder(self.config["document_folder"])
                if result.get("status") == "success":
                    print(f"   ✅ Indexed {result['chunks']} chunks from {result['sources']} sources.")
                    self.config["initial_index_done"] = True
                else:
                    print(f"   ⚠️  {result.get('error', 'Indexing issue')}")
            except ImportError as e:
                print(f"   ⚠️  Cannot import rag_engine: {e}")
                print("   Please install dependencies first:")
                print("   pip install -r requirements.txt")
        print()

    def _print_setup_complete(self) -> None:
        """Print setup completion message."""
        print("─" * 55)
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                                                              ║")
        print("║        ✅  Setup Complete! Welcome to ai4sustainablex       ║")
        print("║                                                              ║")
        print("║   🚀 Quick Start Commands:                                  ║")
        print("║                                                              ║")
        print("║   python cli.py status          Check status                ║")
        print("║   python cli.py ask \"query\"     Ask a question              ║")
        print("║   python cli.py search \"query\"  Semantic search              ║")
        print("║   python cli.py report          Generate a report           ║")
        print("║   python cli.py templates       List report templates       ║")
        print("║   python cli.py providers       Manage LLM providers        ║")
        print("║                                                              ║")
        print("║   🌐 Web: https://sustainablex.in                           ║")
        print("║   📧 Support: info@sustainablex.in                          ║")
        print("║                                                              ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

    def _load_existing_config(self) -> None:
        """Load existing configuration if present."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
                print("📂 Loaded existing configuration.")
            except Exception:
                self.config = {}

    def _save_config(self) -> None:
        """Save configuration to disk."""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)
        print(f"💾 Configuration saved to {CONFIG_FILE}")
        print(f"   You can edit this file directly or re-run setup.\n")


def run_setup() -> Dict[str, Any]:
    """Convenience function to run the setup wizard."""
    wizard = SetupWizard()
    return wizard.run()


if __name__ == "__main__":
    run_setup()