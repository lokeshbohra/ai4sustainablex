"""
ai4sustainablex — Document to Markdown Converter
Converts PDF, DOCX, XLSX, PPTX, TXT files to .md per company.
All knowledge base in the workspace is stored as .md files.
"""

import os
import json
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime


class DocToMarkdownConverter:
    """
    Converts user documents to Markdown (.md) files stored per company.

    Supported input formats: .pdf, .docx, .txt, .pptx, .xlsx
    Output: workspace/companies/{company}/documents/{original_name}.md

    This ensures all indexed knowledge is in a consistent .md format.
    """

    def __init__(self):
        pass

    def convert_folder(self, source_folder: str, company: str,
                       workspace_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert all supported files in a folder to .md files for a company.

        Args:
            source_folder: Path to user's document folder
            company: Company name (sanitized for directory)
            workspace_path: Root workspace path

        Returns:
            Dict with conversion stats
        """
        from company_manager import get_company_manager
        cm = get_company_manager(workspace_path)
        sanitized = cm.sanitize_name(company)
        target_dir = os.path.join(cm.company_dir, sanitized, "documents")
        os.makedirs(target_dir, exist_ok=True)

        source_path = Path(source_folder)
        if not source_path.exists():
            return {"error": f"Source folder not found: {source_folder}", "converted": 0}

        converted = 0
        skipped = 0
        errors = []

        supported_extensions = {
            ".pdf": self._convert_pdf,
            ".docx": self._convert_docx,
            ".txt": self._convert_txt,
            ".pptx": self._convert_pptx,
            ".xlsx": self._convert_xlsx,
        }

        for ext, converter in supported_extensions.items():
            for file_path in source_path.rglob(f"*{ext}"):
                try:
                    output_name = file_path.stem + ".md"
                    output_path = os.path.join(target_dir, output_name)

                    # Skip if already converted and newer
                    if os.path.exists(output_path):
                        src_mtime = os.path.getmtime(str(file_path))
                        out_mtime = os.path.getmtime(output_path)
                        if out_mtime >= src_mtime:
                            skipped += 1
                            continue

                    markdown_content = converter(str(file_path), str(file_path.name))
                    if markdown_content:
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(markdown_content)
                        converted += 1
                except Exception as e:
                    errors.append({"file": str(file_path), "error": str(e)})
                    skipped += 1

        return {
            "status": "success",
            "source_folder": source_folder,
            "target_dir": target_dir,
            "converted": converted,
            "skipped": skipped,
            "errors": errors[:10],
            "total_processed": converted + skipped,
        }

    def _convert_pdf(self, file_path: str, filename: str) -> str:
        """Convert PDF to Markdown."""
        try:
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            md = f"# {filename}\n\n"
            md += f"*Converted from PDF: {file_path}*\n"
            md += f"*Date: {datetime.now().isoformat()}*\n\n---\n\n"

            for i, page in enumerate(pages):
                md += f"\n## Page {i+1}\n\n"
                md += page.page_content + "\n"

            return md
        except ImportError:
            return self._fallback_extract(file_path, filename)

    def _convert_docx(self, file_path: str, filename: str) -> str:
        """Convert DOCX to Markdown."""
        try:
            from docx import Document
            doc = Document(file_path)

            md = f"# {filename}\n\n"
            md += f"*Converted from DOCX: {file_path}*\n"
            md += f"*Date: {datetime.now().isoformat()}*\n\n---\n\n"

            for para in doc.paragraphs:
                if para.style.name.startswith("Heading"):
                    level = para.style.name.split()[-1]
                    try:
                        level = int(level)
                    except ValueError:
                        level = 1
                    md += f"{'#' * min(level, 4)} {para.text}\n\n"
                else:
                    if para.text.strip():
                        md += f"{para.text}\n\n"

            # Extract tables
            for table in doc.tables:
                md += "\n| " + " | ".join(
                    cell.text.strip()[:50] for cell in table.rows[0].cells
                ) + " |\n"
                md += "| " + " | ".join(["---"] * len(table.rows[0].cells)) + " |\n"
                for row in table.rows[1:]:
                    md += "| " + " | ".join(
                        cell.text.strip()[:50] for cell in row.cells
                    ) + " |\n"
                md += "\n"

            return md
        except ImportError:
            return self._fallback_extract(file_path, filename)

    def _convert_txt(self, file_path: str, filename: str) -> str:
        """Convert TXT to Markdown."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        md = f"# {filename}\n\n"
        md += f"*Converted from TXT: {file_path}*\n\n---\n\n"
        md += content
        return md

    def _convert_pptx(self, file_path: str, filename: str) -> str:
        """Convert PPTX to Markdown."""
        try:
            from pptx import Presentation
            prs = Presentation(file_path)

            md = f"# {filename}\n\n"
            md += f"*Converted from PPTX: {file_path}*\n"
            md += f"*Date: {datetime.now().isoformat()}*\n\n---\n\n"

            for i, slide in enumerate(prs.slides, 1):
                md += f"\n## Slide {i}\n\n"
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for para in shape.text_frame.paragraphs:
                            if para.text.strip():
                                md += f"{para.text}\n"
                md += "\n---\n"

            return md
        except ImportError:
            return f"# {filename}\n\n*PPTX file: {file_path}*\n\n*Install python-pptx to convert.*"

    def _convert_xlsx(self, file_path: str, filename: str) -> str:
        """Convert XLSX to Markdown table."""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)

            md = f"# {filename}\n\n"
            md += f"*Converted from XLSX: {file_path}*\n"
            md += f"*Date: {datetime.now().isoformat()}*\n\n---\n\n"

            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                md += f"\n## Sheet: {sheet_name}\n\n"

                # Convert first 50 rows to markdown table
                rows = list(ws.iter_rows(max_row=min(ws.max_row, 50), values_only=True))
                if rows:
                    # Header
                    headers = [str(c) if c else "" for c in rows[0]]
                    md += "| " + " | ".join(h[:40] for h in headers) + " |\n"
                    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

                    for row in rows[1:]:
                        cells = [str(c)[:60] if c else "" for c in row]
                        md += "| " + " | ".join(cells) + " |\n"

                    md += f"\n*({len(rows)-1} data rows shown)*\n"

            return md
        except ImportError:
            return f"# {filename}\n\n*XLSX file: {file_path}*\n\n*Install openpyxl to convert.*"

    def _fallback_extract(self, file_path: str, filename: str) -> str:
        """Fallback text extraction."""
        md = f"# {filename}\n\n"
        md += f"*File: {file_path}*\n"
        md += f"*Date: {datetime.now().isoformat()}*\n\n---\n\n"
        md += f"*Unable to extract text. Install required Python packages (pypdf, python-docx, etc.)*\n"
        return md

    def get_converted_documents(self, company: str,
                                workspace_path: Optional[str] = None) -> List[Dict[str, str]]:
        """List all converted .md documents for a company."""
        from company_manager import get_company_manager
        cm = get_company_manager(workspace_path)
        sanitized = cm.sanitize_name(company)
        docs_dir = os.path.join(cm.company_dir, sanitized, "documents")

        if not os.path.exists(docs_dir):
            return []

        docs = []
        for md_file in sorted(os.listdir(docs_dir)):
            if md_file.endswith(".md"):
                filepath = os.path.join(docs_dir, md_file)
                size = os.path.getsize(filepath)
                docs.append({
                    "filename": md_file,
                    "path": filepath,
                    "size_kb": round(size / 1024, 1),
                })
        return docs

    def get_document_content(self, company: str, filename: str,
                             workspace_path: Optional[str] = None) -> Optional[str]:
        """Read the content of a converted .md document."""
        from company_manager import get_company_manager
        cm = get_company_manager(workspace_path)
        sanitized = cm.sanitize_name(company)
        filepath = os.path.join(cm.company_dir, sanitized, "documents", filename)

        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()