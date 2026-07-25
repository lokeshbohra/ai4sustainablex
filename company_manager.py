"""
ai4sustainablex — Company Manager
Manages companies in the workspace directory as .md files.
Each company has its own subdirectory with documents, context, and reports.
"""

import os
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

COMPANY_INDEX_FILE = "companies"
DEFAULT_WORKSPACE = os.path.expanduser("~/ai4sustainablex_workspace")


class CompanyManager:
    """
    Manages companies in the workspace.

    Workspace structure:
        workspace/
        └── companies/
            ├── Acme_Corp/
            │   ├── company.md          # Company profile + context
            │   ├── documents/          # .md files converted from source docs
            │   └── reports/            # Generated reports
            └── Another_Company/
                └── ...
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or self._get_default_workspace()
        self._ensure_workspace()

    def _get_default_workspace(self) -> str:
        """Get the default workspace directory from config or fallback."""
        config_path = os.path.expanduser("~/.ai4sustainablex/config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                return config.get("workspace_path", DEFAULT_WORKSPACE)
            except Exception:
                pass
        return DEFAULT_WORKSPACE

    def _ensure_workspace(self) -> None:
        """Create workspace directories if they don't exist."""
        os.makedirs(self.company_dir, exist_ok=True)

    @property
    def company_dir(self) -> str:
        """Get the companies directory path."""
        return os.path.join(self.workspace_path, "companies")

    @property
    def output_dir(self) -> str:
        return os.path.join(self.workspace_path, "output")

    @property
    def vector_db_dir(self) -> str:
        return os.path.join(self.workspace_path, "vector_db")

    def sanitize_name(self, name: str) -> str:
        """Convert company name to a safe directory name."""
        return name.replace(" ", "_").replace("/", "_").replace("\\", "_")

    def list_companies(self) -> List[Dict[str, Any]]:
        """List all companies in the workspace."""
        companies = []
        if not os.path.exists(self.company_dir):
            return companies

        for company_dir in sorted(os.listdir(self.company_dir)):
            comp_path = os.path.join(self.company_dir, company_dir)
            md_file = os.path.join(comp_path, "company.md")
            if os.path.isdir(comp_path):
                info = {
                    "directory": company_dir,
                    "path": comp_path,
                    "has_profile": os.path.exists(md_file),
                }
                if info["has_profile"]:
                    try:
                        context = self._read_company_context(comp_path)
                        info["companyName"] = context.get("companyName", company_dir)
                        info["context"] = context.get("context", "")
                        info["documents_count"] = context.get("documents_count", 0)
                        info["reports_count"] = context.get("reports_count", 0)
                        info["created_at"] = context.get("created_at", "")
                    except Exception:
                        info["companyName"] = company_dir.replace("_", " ")
                else:
                    info["companyName"] = company_dir.replace("_", " ")

                # Count documents and reports
                docs_dir = os.path.join(comp_path, "documents")
                reports_dir = os.path.join(comp_path, "reports")
                if not info.get("documents_count"):
                    info["documents_count"] = len(list(Path(docs_dir).glob("*.md"))) if os.path.exists(docs_dir) else 0
                if not info.get("reports_count"):
                    info["reports_count"] = len(list(Path(reports_dir).glob("*.md"))) if os.path.exists(reports_dir) else 0

                companies.append(info)
        return companies

    def get_company(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific company's information."""
        sanitized = self.sanitize_name(name)
        comp_path = os.path.join(self.company_dir, sanitized)

        if not os.path.exists(comp_path):
            return None

        context = self._read_company_context(comp_path)
        result = {
            "directory": sanitized,
            "path": comp_path,
            "companyName": context.get("companyName", name),
            "context": context.get("context", ""),
            "created_at": context.get("created_at", ""),
            "documents_count": len(list(Path(os.path.join(comp_path, "documents")).glob("*.md")))
            if os.path.exists(os.path.join(comp_path, "documents")) else 0,
            "reports_count": len(list(Path(os.path.join(comp_path, "reports")).glob("*.md")))
            if os.path.exists(os.path.join(comp_path, "reports")) else 0,
        }
        return result

    def add_company(self, name: str, context: str = "") -> Dict[str, Any]:
        """Add a new company to the workspace."""
        sanitized = self.sanitize_name(name)
        comp_path = os.path.join(self.company_dir, sanitized)

        if os.path.exists(comp_path):
            return {
                "success": False,
                "message": f"Company '{name}' already exists.",
                "directory": sanitized,
            }

        # Create company directory structure
        os.makedirs(os.path.join(comp_path, "documents"), exist_ok=True)
        os.makedirs(os.path.join(comp_path, "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.vector_db_dir, sanitized), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, sanitized), exist_ok=True)

        # Write company.md
        now = datetime.now().isoformat()
        company_md = f"""---
companyName: {name}
created_at: {now}
documents_count: 0
reports_count: 0
---

# {name}

## Context
{context or 'No additional context provided.'}

## Documents
*Index your documents to populate this section.*

## Reports
*Generate reports to populate this section.*
"""
        with open(os.path.join(comp_path, "company.md"), "w") as f:
            f.write(company_md)

        return {
            "success": True,
            "message": f"Company '{name}' created successfully.",
            "directory": sanitized,
            "path": comp_path,
            "companyName": name,
        }

    def update_company_context(self, name: str, context: str) -> Dict[str, Any]:
        """Update the context/description for a company."""
        sanitized = self.sanitize_name(name)
        comp_path = os.path.join(self.company_dir, sanitized)

        if not os.path.exists(comp_path):
            return {"success": False, "message": f"Company '{name}' not found."}

        md_file = os.path.join(comp_path, "company.md")
        existing = self._read_company_context(comp_path)

        updated_md = f"""---
companyName: {name}
created_at: {existing.get('created_at', datetime.now().isoformat())}
documents_count: {existing.get('documents_count', 0)}
reports_count: {existing.get('reports_count', 0)}
updated_at: {datetime.now().isoformat()}
---

# {name}

## Context
{context}
"""
        with open(md_file, "w") as f:
            f.write(updated_md)

        return {"success": True, "message": f"Context updated for '{name}'."}

    def remove_company(self, name: str) -> Dict[str, Any]:
        """Remove a company and its data from the workspace."""
        sanitized = self.sanitize_name(name)
        comp_path = os.path.join(self.company_dir, sanitized)

        if not os.path.exists(comp_path):
            return {"success": False, "message": f"Company '{name}' not found."}

        import shutil
        shutil.rmtree(comp_path)
        return {"success": True, "message": f"Company '{name}' removed."}

    def get_documents_dir(self, name: str) -> Optional[str]:
        """Get the documents directory for a company."""
        sanitized = self.sanitize_name(name)
        docs_dir = os.path.join(self.company_dir, sanitized, "documents")
        if os.path.exists(docs_dir):
            return docs_dir
        return None

    def get_reports_dir(self, name: str) -> Optional[str]:
        """Get the reports directory for a company."""
        sanitized = self.sanitize_name(name)
        reports_dir = os.path.join(self.company_dir, sanitized, "reports")
        if os.path.exists(reports_dir):
            return reports_dir
        return None

    def get_output_dir(self, name: str) -> str:
        """Get the output directory for a company."""
        sanitized = self.sanitize_name(name)
        out_dir = os.path.join(self.output_dir, sanitized)
        os.makedirs(out_dir, exist_ok=True)
        return out_dir

    def get_vector_db_dir(self, name: str) -> str:
        """Get the vector DB directory for a company."""
        sanitized = self.sanitize_name(name)
        vec_dir = os.path.join(self.vector_db_dir, sanitized)
        os.makedirs(vec_dir, exist_ok=True)
        return vec_dir

    def get_context(self, name: str) -> str:
        """Get the context text for a company."""
        sanitized = self.sanitize_name(name)
        comp_path = os.path.join(self.company_dir, sanitized)
        data = self._read_company_context(comp_path)
        return data.get("context", "")

    def increment_report_count(self, name: str) -> None:
        """Increment the report counter for a company."""
        sanitized = self.sanitize_name(name)
        comp_path = os.path.join(self.company_dir, sanitized)
        md_file = os.path.join(comp_path, "company.md")

        existing = self._read_company_context(comp_path)
        count = existing.get("reports_count", 0) + 1

        # Update frontmatter
        content = self._read_raw_company_md(comp_path)
        if content:
            updated = content.replace(
                f"reports_count: {existing.get('reports_count', 0)}",
                f"reports_count: {count}",
            )
            with open(md_file, "w") as f:
                f.write(updated)

    def _read_company_context(self, comp_path: str) -> Dict[str, Any]:
        """Parse frontmatter from company.md."""
        md_file = os.path.join(comp_path, "company.md")
        if not os.path.exists(md_file):
            return {}

        data = {}
        with open(md_file, "r") as f:
            content = f.read()

        # Parse YAML frontmatter
        lines = content.split("\n")
        in_frontmatter = False
        body_lines = []
        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    in_frontmatter = False
                    continue
            if in_frontmatter:
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"')
                    try:
                        data[key] = int(val)
                    except ValueError:
                        data[key] = val
            else:
                body_lines.append(line)

        if not data.get("context"):
            # Extract context from body
            context_started = False
            context_lines = []
            for line in body_lines:
                if line.strip().startswith("## Context"):
                    context_started = True
                    continue
                if context_started:
                    if line.strip().startswith("## ") or line.strip().startswith("# "):
                        break
                    context_lines.append(line)
            data["context"] = "\n".join(context_lines).strip()

        return data

    def _read_raw_company_md(self, comp_path: str) -> str:
        """Read the raw company.md content."""
        md_file = os.path.join(comp_path, "company.md")
        if not os.path.exists(md_file):
            return ""
        with open(md_file, "r") as f:
            return f.read()


# Convenience function
def get_company_manager(workspace_path: Optional[str] = None) -> CompanyManager:
    return CompanyManager(workspace_path)