# ai4sustainablex — Copyright (c) 2026 SustainableX
# License: BUSL 1.1 — https://sustainablex.in/license
# Free for personal and internal corporate use.
"""ai4sustainablex CLI — Open Core Edition"""

import os, json, sys, subprocess
from typing import Optional
import click, requests

API_URL = os.getenv("AI4SX_API_URL", "http://localhost:8000")

BRAND_HEADER = """
╔══════════════════════════════════════════════════════════════╗
║        🌱  ai4sustainablex  —  ESG Reporting Toolkit        ║
║   Local-First • Private • Open Source                        ║
║   https://sustainablex.in  |  info@sustainablex.in           ║
╚══════════════════════════════════════════════════════════════╝
"""

BRAND_FOOTER = """
──────────────────────────────────────────────────────────────
🌐 sustainablex.in  |  📧 info@sustainablex.in
Built for ESG practitioners. Data stays on your machine.
"""

PREMIUM_NOTE = "\n🔒 Framework Template Library. Run 'python cli.py unlock' or see COMMERCIAL.md.\n"

def _ensure_server():
    try:
        if requests.get(f"{API_URL}/health", timeout=2).status_code == 200: return True
    except: pass
    click.echo("⚠️  Backend server is not running on port 8000.")
    if click.confirm("Start it now?", default=True):
        subprocess.Popen([sys.executable, "main.py"], cwd=os.path.dirname(os.path.abspath(__file__)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import time
        for _ in range(15):
            time.sleep(1)
            try:
                if requests.get(f"{API_URL}/health", timeout=1).status_code == 200:
                    click.echo("✅ Server started."); return True
            except: pass
        click.echo("❌ Server failed to start. Run 'python main.py' manually.")
        return False
    click.echo("❌ Cannot continue without the backend server.")
    return False

@click.group()
@click.version_option(version="1.0.0", prog_name="ai4sustainablex")
def cli():
    """🌱 ai4sustainablex — ESG drafts from your documents — cited, gap-flagged, local."""

@cli.command()
def setup():
    """Run the interactive first-time setup wizard."""
    try:
        from setup_wizard import run_setup; run_setup()
    except ImportError:
        click.echo("⚠️  setup_wizard.py not found.")

@cli.command()
def status():
    if not _ensure_server(): return
    try:
        data = requests.get(f"{API_URL}/status").json()
        config = data.get("config", {})
        rag = data.get("rag_engine", {})
        click.echo(f"\n📊 Status: Provider={config.get('llm_provider','?')} | Indexed={rag.get('total_chunks',0)} chunks | Sources={rag.get('unique_sources',0)}")
    except Exception as e: click.echo(f"❌ {e}")
    click.echo(BRAND_FOOTER)

@cli.command()
@click.argument("folder", required=False)
def init(folder):
    if not _ensure_server(): return
    if not folder:
        cfg_path = os.path.expanduser("~/.ai4sustainablex/config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path) as f: folder = json.load(f).get("document_folder")
        if not folder: click.echo("❌ No folder. Run 'ai4sustainablex setup' first."); return
    folder = os.path.expanduser(folder)
    click.echo(f"📁 Indexing: {folder}")
    try:
        resp = requests.post(f"{API_URL}/index", json={"folder_path": folder})
        data = resp.json()
        click.echo(f"✅ Indexed {data.get('chunks',0)} chunks from {data.get('sources',0)} sources.")
    except Exception as e: click.echo(f"❌ {e}")
    click.echo(BRAND_FOOTER)

@cli.command()
@click.argument("query")
@click.option("--top-k", default=10)
@click.option("--search-type", default="hybrid", type=click.Choice(["hybrid","bm25","dense"]))
def ask(query, top_k, search_type):
    if not _ensure_server(): return
    click.echo(f"\n🤔 {query}\n{'─'*60}")
    try:
        data = requests.post(f"{API_URL}/chat", json={"query":query,"top_k":top_k,"search_type":search_type}).json()
        click.echo(f"\n{data.get('answer','')}\n")
        for i, src in enumerate(data.get("sources",[])[:5], 1):
            click.echo(f"  {i}. {src.get('filename','?')} — P.{src.get('page','?')}")
    except Exception as e: click.echo(f"❌ {e}")
    click.echo(BRAND_FOOTER)

@cli.command()
@click.argument("query")
@click.option("--top-k", default=10)
@click.option("--search-type", default="hybrid", type=click.Choice(["hybrid","bm25","dense"]))
def search(query, top_k, search_type):
    if not _ensure_server(): return
    click.echo(f"\n🔍 {query}\n{'─'*60}")
    try:
        results = requests.post(f"{API_URL}/search", json={"query":query,"top_k":top_k,"search_type":search_type}).json().get("local_results",[])
        for i, r in enumerate(results, 1):
            m = r.get("metadata",{})
            click.echo(f"\n📄 {i} — {m.get('filename','?')} P.{m.get('page','?')} | {r.get('score',0)}")
            click.echo(f"   {r.get('text','')[:200]}...")
        if not results: click.echo("No results. Index first: ai4sustainablex init")
    except Exception as e: click.echo(f"❌ {e}")
    click.echo(BRAND_FOOTER)

@cli.command()
@click.option("--template","-t", default="esg-report-basic")
@click.option("--query","-q", default="")
@click.option("--company","-c", default="")
@click.option("--period","-p", default="")
@click.option("--format","-f", default="markdown", type=click.Choice(["markdown","pdf","docx"]))
def report(template, query, company, period, format):
    if not _ensure_server(): return
    fields = {}
    if company: fields["company_name"] = company
    if period: fields["reporting_period"] = period
    click.echo(f"\n📝 Generating {template}...")
    try:
        data = requests.post(f"{API_URL}/generate_report", json={"template_id":template,"query":query,"fields":fields,"output_format":format}).json()
        if data.get("status")=="success":
            click.echo(f"✅ Saved: {data['report_path']}")
        else: click.echo(f"❌ {data}")
    except Exception as e: click.echo(f"❌ {e}")
    click.echo(BRAND_FOOTER)

@cli.command()
@click.option("--free", "free_only", is_flag=True)
def templates(free_only):
    """List available templates (4 free + premium available)."""
    if not _ensure_server():
        from templates.template_registry import get_template_registry
        registry = get_template_registry()
        click.echo(f"\n📋 {registry.count()['total']} templates ({registry.count()['free']} free + {registry.count()['premium']} premium)")
        for t in registry.list_all():
            click.echo(f"  {'🆓' if not t.get('is_premium') else '🔒'} {t['id']:30s} {t['name']}")
        click.echo(BRAND_FOOTER); return
    try:
        data = requests.get(f"{API_URL}/templates").json()
        for t in data.get("templates",[]):
            badge = "🔒" if t.get("is_premium") else "🆓"
            click.echo(f"  {badge} {t['id']:30s} {t['name']}")
    except Exception as e: click.echo(f"❌ {e}")
    click.echo(BRAND_FOOTER)

@cli.group()
def providers(): pass

@providers.command("list")
def providers_list():
    click.echo("🤖 Providers: ollama (default) | openai | anthropic | deepseek | gemini | kimi | grok | groq | openrouter | glm | qwen")
    click.echo("   Switch: python cli.py providers switch <name>")

@providers.command("switch")
@click.argument("provider")
@click.option("--model","-m", default=None)
def providers_switch(provider, model):
    if not _ensure_server(): return
    try:
        data = requests.post(f"{API_URL}/providers/switch", json={"provider":provider,"model":model}).json()
        click.echo(f"✅ {data.get('provider')} ({data.get('model')})")
    except Exception as e: click.echo(f"❌ {e}")

@cli.group()
def company(): pass

@company.command("list")
def company_list():
    from company_manager import get_company_manager
    companies = get_company_manager().list_companies()
    if not companies: click.echo("No companies. Add: ai4sustainablex company add \"Name\""); return
    for c in companies: click.echo(f"  📁 {c['companyName']} | Docs: {c.get('documents_count',0)} | Reports: {c.get('reports_count',0)}")

@company.command("add")
@click.argument("name")
def company_add(name):
    from company_manager import get_company_manager
    result = get_company_manager().add_company(name)
    click.echo(f"{'✅' if result['success'] else '❌'} {result['message']}")

@company.command("select")
@click.argument("name")
def company_select(name):
    cfg_path = os.path.expanduser("~/.ai4sustainablex/config.json")
    config = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    config["current_company"] = name
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    json.dump(config, open(cfg_path,"w"), indent=2)
    click.echo(f"✅ Company set to: {name}")

@cli.group()
def config(): pass

@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    cfg_path = os.path.expanduser("~/.ai4sustainablex/config.json")
    if not os.path.exists(cfg_path): click.echo("No config."); return
    cfg = json.load(open(cfg_path))
    if key: click.echo(f"{key}: {cfg.get(key,'not set')}")
    else: click.echo(json.dumps({k:v for k,v in cfg.items() if "api_key" not in k}, indent=2))

@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    cfg_path = os.path.expanduser("~/.ai4sustainablex/config.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    if value.lower() in ("true","yes"): value = True
    elif value.lower() in ("false","no"): value = False
    cfg[key] = value
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    json.dump(cfg, open(cfg_path,"w"), indent=2)
    click.echo(f"✅ {key} = {value}")

@cli.command()
def usage():
    from usage_stats import get_usage_tracker
    stats = get_usage_tracker().get_stats()
    click.echo(f"\n📊 Sessions: {stats.get('total_sessions',0)} | Tokens: {stats.get('total_tokens_used',0):,} | Reports: {stats.get('total_reports_generated',0)}")
    click.echo(BRAND_FOOTER)

@cli.command()
def ui():
    if not _ensure_server(): return
    import webbrowser; webbrowser.open("http://localhost:8000/docs")

# ─── Premium features (stubs — redirect to unlock) ─────────────────

@cli.command()
@click.option("--key","-k", default=None)
def unlock(key):
    click.echo("""
🔒 Framework Template Library — $99 one-time

Unlocks the full framework library: GRI 2021, SBTi, CDP, IFRS S1/S2,
CSRD/ESRS, CSDDD (+ supply chain), AFOLU/FLAG/REDD+, BRSR,
Africa Climate-Gender, compliance checklist, carbon footprint,
and task outputs (social posts, newsletters, disclosures).

Need board-ready rigor? Add SustainableX Validation (from $500/report
or $200/mo) — claim-level confidence scoring + expert redline.
See COMMERCIAL.md.

📧 Email: info@sustainablex.in
Subject: AI4SX Template Library Unlock

You will receive a payment key within 24 hours.
""")

@cli.command()
@click.option("--company","-c", required=True)
def social(company, **kwargs):
    click.echo(PREMIUM_NOTE)

@cli.command()
@click.option("--company","-c", required=True)
def newsletter(company, **kwargs):
    click.echo(PREMIUM_NOTE)

@cli.command()
@click.option("--company","-c", required=True)
def disclosure(company, **kwargs):
    click.echo(PREMIUM_NOTE)

if __name__ == "__main__":
    print(BRAND_HEADER)
    cli()