# ai4sustainablex — Copyright (c) 2026 SustainableX
# License: BUSL 1.1 — https://sustainablex.in/license
# Free for personal and internal corporate use.
"""ai4sustainablex Core — FastAPI Backend (Open Core Edition)"""

import os, json
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="ai4sustainablex Core", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

CONFIG_DIR = os.path.expanduser("~/.ai4sustainablex")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
WORKSPACE_DIR = os.path.expanduser("~/ai4sustainablex_workspace")
_rag_engine = _llm_provider = _knowledge_graph = _search_connector = None
_config = {}

def _get_workspace_path():
    return (json.load(open(CONFIG_FILE)) if os.path.exists(CONFIG_FILE) else {}).get("workspace_path", WORKSPACE_DIR)

def _load_config():
    global _config
    if os.path.exists(CONFIG_FILE):
        try: _config = json.load(open(CONFIG_FILE))
        except: pass
    return _config

def _get_rag_engine():
    global _rag_engine
    if _rag_engine is None:
        from rag_engine import HybridRAGEngine
        ws = _get_workspace_path()
        _rag_engine = HybridRAGEngine(storage_path=os.path.join(ws, "vector_db"))
        _rag_engine._load_index()
    return _rag_engine

def _get_llm_provider():
    global _llm_provider
    if _llm_provider is None:
        from llm_providers.ollama_provider import OllamaProvider
        from llm_providers.base_provider import ProviderConfig, ProviderType
        config = _load_config()
        model = config.get("ollama_model", "llama3.2:1b")
        _llm_provider = OllamaProvider(ProviderConfig(name="ollama", provider_type=ProviderType.LOCAL, model=model, base_url="http://localhost:11434", temperature=0.2, max_tokens=4096))
    return _llm_provider

# Core-only template registry (4 free templates only)
CORE_TEMPLATES = {
    "esg-report-basic": {"name":"Basic ESG Report","framework":"GRI","sections":["Executive Summary","Environmental","Social","Governance"]},
    "ghg-emissions": {"name":"GHG Emissions Analysis","framework":"GRI","sections":["Executive Summary","Scope 1","Scope 2","Scope 3"]},
    "sustainability-brief": {"name":"Sustainability Brief","framework":"Multi","sections":["Highlights","Performance","Risks","Commitments"]},
    "sme-readiness": {"name":"SME ESG Readiness","framework":"SME","sections":["Profile","Practices","Gap Analysis","Roadmap"]},
}

class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=10, ge=1, le=50)
    search_type: str = Field(default="hybrid", pattern="^(hybrid|bm25|dense)$")
    include_web: bool = False

class IndexRequest(BaseModel):
    folder_path: str
    company: str = ""

class ReportRequest(BaseModel):
    template_id: str = "esg-report-basic"
    query: str = ""
    fields: Dict[str, str] = Field(default_factory=dict)
    output_format: str = Field(default="markdown", pattern="^(markdown|pdf|docx)$")

@app.get("/")
async def root():
    return {"name":"ai4sustainablex Core","version":"1.0.0","website":"https://sustainablex.in","support":"info@sustainablex.in","note":"Premium features require the engine module. Run: python cli.py unlock"}

@app.get("/health")
async def health():
    return {"status":"healthy","timestamp":datetime.now().isoformat()}

@app.get("/status")
async def status():
    config = _load_config()
    rag = _get_rag_engine()
    return {"config":{"llm_provider":config.get("llm_provider","ollama"),"document_folder":config.get("document_folder","not set")},"rag_engine":rag.get_stats()}

@app.post("/index")
async def index_folder(req: IndexRequest):
    if not os.path.exists(req.folder_path): raise HTTPException(404, f"Folder not found: {req.folder_path}")
    rag = _get_rag_engine()
    result = rag.index_folder(req.folder_path)
    if req.company and result.get("status")=="success":
        try:
            from doc_to_md_converter import DocToMarkdownConverter
            conv = DocToMarkdownConverter().convert_folder(req.folder_path, req.company, workspace_path=_get_workspace_path())
            result["converted_count"] = conv.get("converted",0)
        except: pass
    return result

@app.post("/search")
async def search(req: QueryRequest):
    rag = _get_rag_engine()
    results = rag.search(req.query, top_k=req.top_k, search_type=req.search_type)
    return {"query":req.query,"search_type":req.search_type,"local_results":results,"local_count":len(results)}

@app.post("/chat")
async def chat(req: QueryRequest):
    rag = _get_rag_engine()
    llm = _get_llm_provider()
    results = rag.search(req.query, top_k=req.top_k)
    if not results: return {"answer":"No relevant documents found. Index your ESG documents first.","sources":[]}
    context_chunks = [r["text"] for r in results]
    answer = llm.generate_with_context(query=req.query, context_chunks=context_chunks)
    return {"query":req.query,"answer":answer,"sources":[{"source":r["metadata"].get("source"),"filename":r["metadata"].get("filename"),"page":r["metadata"].get("page",0)} for r in results],"model":llm.config.model}

@app.post("/generate_report")
async def generate_report(req: ReportRequest):
    """Generate a basic ESG report using the core engine only. Premium templates require the engine module."""
    rag = _get_rag_engine()
    llm = _get_llm_provider()
    tmpl = CORE_TEMPLATES.get(req.template_id, CORE_TEMPLATES["esg-report-basic"])
    results = rag.search(f"{req.query} {tmpl['name']}", top_k=10)
    if not results: return {"status":"error","error":"No documents indexed"}
    context = "\n\n".join([r["text"] for r in results])
    prompt = f"Generate a {tmpl['name']} report for {req.fields.get('company_name','Unknown')} using this context:\n\n{context[:4000]}\n\nSections: {', '.join(tmpl['sections'])}"
    content = llm.generate(prompt)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(_get_workspace_path(),"output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"report_{req.template_id}_{timestamp}.md")
    with open(path,"w") as f: f.write(content)
    return {"status":"success","report_path":path,"content":content}

@app.get("/templates")
async def list_templates():
    return {"templates":[{"id":k,"name":v["name"],"framework":v["framework"],"is_premium":False,"accessible":True,"sections_count":len(v["sections"])} for k,v in CORE_TEMPLATES.items()],"counts":{"total":4,"free":4,"premium":0},"note":"13+ premium templates available in the engine. Run: python cli.py unlock"}

@app.get("/templates/{template_id}")
async def get_template(template_id: str):
    if template_id not in CORE_TEMPLATES: raise HTTPException(404)
    return {"id":template_id,**CORE_TEMPLATES[template_id]}

@app.get("/payments/status")
async def payment_status():
    return {"unlocked":False,"message":"Premium features require the engine module. Contact info@sustainablex.in for enterprise access."}

@app.post("/payments/unlock")
async def payment_unlock(key: str = Query(...)):
    return {"success":False,"message":"Unlock is available in the full engine. Contact info@sustainablex.in"}

@app.get("/companies")
async def list_companies():
    from company_manager import get_company_manager
    return {"companies": get_company_manager().list_companies()}

@app.get("/config")
async def get_config():
    return {k:v for k,v in _load_config().items() if "api_key" not in k}

@app.get("/usage")
async def get_usage():
    from usage_stats import get_usage_tracker
    return get_usage_tracker().get_stats()

if __name__ == "__main__":
    import uvicorn
    print("🌱 ai4sustainablex Core — http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)