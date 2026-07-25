"""
ai4sustainablex — Hybrid RAG Engine
Combines BM25 (keyword) + Dense FAISS (semantic) retrieval with
weighted average ranking for improved accuracy and reduced hallucination.

Also builds page-level metadata index for source referencing.
"""

import os
import pickle
import json
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, Docx2txtLoader,
    UnstructuredPowerPointLoader, UnstructuredExcelLoader,
)


class HybridRAGEngine:
    """
    Hybrid retrieval engine combining BM25 keyword search and dense FAISS semantic search.

    Retrieval Pipeline:
    1. User query → Dense embedding → FAISS cosine similarity
    2. User query → BM25 token-level matching
    3. Fused results via weighted reciprocal rank fusion (RRF)
    4. Returns deduplicated, ranked results with source metadata

    Supports PDF, DOCX, TXT, PPTX, XLSX file formats.
    """

    def __init__(self, storage_path: str = "./storage/vector_db",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the hybrid RAG engine.

        Args:
            storage_path: Directory for vector index + metadata storage
            embedding_model: SentenceTransformer model name for dense embeddings
        """
        self.storage_path = storage_path
        self.embedding_model_name = embedding_model
        os.makedirs(storage_path, exist_ok=True)

        # Lazy-init components
        self.embedding_model: Optional[SentenceTransformer] = None
        self.faiss_index: Optional[faiss.Index] = None
        self.bm25: Optional[BM25Okapi] = None

        # Data stores
        self.documents: List[str] = []       # Raw text chunks
        self.metadata: List[Dict] = []       # Per-chunk metadata (source, page)
        self.document_index: List[str] = []  # Tokenized documents for BM25
        self.page_index: Dict[str, List[int]] = {}  # Source → chunk indices

        # Weights for hybrid ranking (default: 0.4 BM25, 0.6 Dense)
        self.bm25_weight = 0.4
        self.dense_weight = 0.6
        self.dimension = 384  # MiniLM-L6-v2 embedding dimension

        # Page-level reference index
        self.page_references: Dict[str, Dict[int, str]] = {}  # file → page → summary

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the embedding model."""
        if self.embedding_model is None:
            print(f"🧮 Loading embedding model: {self.embedding_model_name}...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
        return self.embedding_model

    # ─── Indexing ───────────────────────────────────────────────

    def index_folder(self, folder_path: str) -> Dict[str, Any]:
        """
        Index all supported documents in a folder.

        Supported formats: .pdf, .docx, .txt, .pptx, .xlsx

        Args:
            folder_path: Path to the document directory

        Returns:
            Dict with indexing stats: count, sources, time
        """
        start_time = datetime.now()
        print(f"📁 Indexing folder: {folder_path}")

        path = Path(folder_path)
        if not path.exists():
            return {"error": f"Folder not found: {folder_path}", "count": 0}

        all_texts, all_metadata = self._load_documents(path)

        if not all_texts:
            return {"error": "No supported documents found", "count": 0}

        # Tokenize for BM25
        print(f"🔤 Building BM25 index for {len(all_texts)} chunks...")
        tokenized = [self._tokenize(text) for text in all_texts]

        # Generate dense embeddings
        print(f"🧮 Generating dense embeddings ({self.dimension}d)...")
        embeddings = self.model.encode(
            all_texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,  # Cosine similarity via inner product
        )

        # Build FAISS index (inner product for normalized vectors = cosine sim)
        self.dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(self.dimension)  # Inner Product
        self.faiss_index.add(embeddings.astype('float32'))

        # Build BM25
        self.bm25 = BM25Okapi(tokenized)

        # Store data
        self.documents = all_texts
        self.metadata = all_metadata
        self.document_index = tokenized

        # Build page-level reference index
        self._build_page_index(all_metadata)

        # Build source→chunks mapping
        for i, meta in enumerate(all_metadata):
            source = meta.get("source", "unknown")
            if source not in self.page_index:
                self.page_index[source] = []
            self.page_index[source].append(i)

        # Persist to disk
        self._save_index()

        elapsed = (datetime.now() - start_time).total_seconds()
        unique_sources = len(set(m.get("source", "") for m in all_metadata))

        result = {
            "status": "success",
            "chunks": len(all_texts),
            "sources": unique_sources,
            "dimension": self.dimension,
            "time_seconds": round(elapsed, 1),
            "storage_path": self.storage_path,
        }
        print(f"✅ Indexed {len(all_texts)} chunks from {unique_sources} sources in {elapsed:.1f}s")
        return result

    def _load_documents(self, path: Path) -> Tuple[List[str], List[Dict]]:
        """Load and chunk all supported documents in a directory tree."""
        loaders = {
            ".pdf": PyPDFLoader,
            ".txt": TextLoader,
            ".docx": Docx2txtLoader,
            ".pptx": UnstructuredPowerPointLoader,
            ".xlsx": UnstructuredExcelLoader,
        }

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        all_texts = []
        all_metadata = []

        for ext, LoaderClass in loaders.items():
            for file_path in path.rglob(f"*{ext}"):
                try:
                    loader = LoaderClass(str(file_path))
                    docs = loader.load()
                    chunks = text_splitter.split_documents(docs)
                    for chunk in chunks:
                        page = chunk.metadata.get("page", 0)
                        all_texts.append(chunk.page_content)
                        all_metadata.append({
                            "source": str(file_path),
                            "filename": file_path.name,
                            "page": page,
                            "chunk_id": len(all_texts),
                            "extension": ext,
                        })
                except Exception as e:
                    print(f"⚠️ Skipping {file_path}: {e}")

        return all_texts, all_metadata

    def _tokenize(self, text: str) -> List[str]:
        """Simple whitespace tokenization for BM25."""
        return text.lower().split()

    # ─── Search & Retrieval ────────────────────────────────────

    def search(self, query: str, top_k: int = 10,
               search_type: str = "hybrid") -> List[Dict[str, Any]]:
        """
        Search indexed documents.

        Args:
            query: Search query string
            top_k: Number of results to return
            search_type: 'hybrid', 'bm25', 'dense', or 'knowledge_graph'

        Returns:
            List of result dicts with: text, metadata, score, rank
        """
        if search_type == "hybrid":
            results, scores = self._hybrid_search(query, top_k)
        elif search_type == "bm25":
            results, scores = self._bm25_search(query, top_k)
        elif search_type == "dense":
            results, scores = self._dense_search(query, top_k)
        else:
            return []

        # Format results
        formatted = []
        for i, (idx, score) in enumerate(zip(results, scores)):
            if idx < len(self.documents):
                formatted.append({
                    "text": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": round(float(score), 4),
                    "rank": i + 1,
                })
        return formatted

    def _hybrid_search(self, query: str, top_k: int) -> Tuple[List[int], List[float]]:
        """
        Hybrid retrieval: BM25 + Dense using weighted Reciprocal Rank Fusion.

        Algorithm:
        1. Run BM25 and Dense search independently
        2. Collect top_k * 2 results from each
        3. Apply RRF: score(doc) = sum(1 / (k + rank_i)) for each retriever
        4. Apply weights to combine: final = w_bm25 * rrf_bm25 + w_dense * rrf_dense
        5. Sort by combined score, return top_k
        """
        # Get extended results from both retrievers
        bm25_indices, bm25_scores = self._bm25_search(query, top_k * 2)
        dense_indices, dense_scores = self._dense_search(query, top_k * 2)

        # RRF constant (typically 60)
        k = 60

        # Build RRF scores
        rrf_scores: Dict[int, float] = {}

        # BM25 RRF
        for rank, idx in enumerate(bm25_indices):
            rrf = 1.0 / (k + rank + 1)
            rrf_scores[idx] = rrf_scores.get(idx, 0) + self.bm25_weight * rrf

        # Dense RRF
        for rank, idx in enumerate(dense_indices):
            rrf = 1.0 / (k + rank + 1)
            rrf_scores[idx] = rrf_scores.get(idx, 0) + self.dense_weight * rrf

        # Sort by combined RRF score (descending)
        sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        final_indices = [idx for idx, _ in sorted_items[:top_k]]
        final_scores = [score for _, score in sorted_items[:top_k]]

        return final_indices, final_scores

    def _bm25_search(self, query: str, top_k: int) -> Tuple[List[int], List[float]]:
        """BM25 keyword-based retrieval."""
        if self.bm25 is None:
            if not self._load_index():
                return [], []
            if self.bm25 is None:
                return [], []

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices (descending by score)
        if len(scores) == 0:
            return [], []

        top_indices = np.argsort(scores)[::-1][:top_k]
        top_scores = scores[top_indices]

        return list(top_indices), list(top_scores)

    def _dense_search(self, query: str, top_k: int) -> Tuple[List[int], List[float]]:
        """Dense (FAISS) semantic retrieval using cosine similarity."""
        if self.faiss_index is None:
            if not self._load_index():
                return [], []
            if self.faiss_index is None:
                return [], []

        query_emb = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype('float32')

        scores, indices = self.faiss_index.search(query_emb, top_k)

        return list(indices[0]), list(scores[0])

    # ─── Knowledge Graph Search ────────────────────────────────

    def search_by_source(self, source_file: str, query: str,
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search within a specific source file only.

        Args:
            source_file: Source file path or filename
            query: Search query
            top_k: Max results

        Returns:
            Filtered search results from that source only
        """
        all_results = self.search(query, top_k=top_k * 3)
        # Filter by matching source (partial match on filename or path)
        filtered = [
            r for r in all_results
            if source_file in r["metadata"].get("source", "")
            or source_file in r["metadata"].get("filename", "")
        ]
        return filtered[:top_k]

    def get_source_summary(self, source_file: str) -> Dict[str, Any]:
        """
        Get summary statistics for a specific indexed source file.

        Args:
            source_file: Source file name or path

        Returns:
            Dict with chunk count, page range, topics
        """
        chunks = []
        for i, meta in enumerate(self.metadata):
            if source_file in meta.get("source", "") or source_file == meta.get("filename", ""):
                chunks.append({
                    "chunk_id": i,
                    "text": self.documents[i][:200] + "..." if len(self.documents[i]) > 200 else self.documents[i],
                    "page": meta.get("page", 0),
                })

        if not chunks:
            return {"source": source_file, "chunks": 0, "message": "Source not found in index"}

        pages = sorted(set(c["page"] for c in chunks))
        return {
            "source": source_file,
            "total_chunks": len(chunks),
            "pages": pages,
            "page_count": len(pages),
            "page_range": f"{pages[0]}-{pages[-1]}" if pages else "N/A",
            "preview_chunks": chunks[:3],
        }

    def get_page_references(self, source_file: str, page: int) -> List[Dict[str, Any]]:
        """
        Get all text chunks from a specific page of a source file.

        Args:
            source_file: Source file name or path
            page: Page number

        Returns:
            List of text chunks on that page
        """
        results = []
        for i, meta in enumerate(self.metadata):
            if (source_file in meta.get("source", "") and
                    meta.get("page") == page):
                results.append({
                    "chunk_id": i,
                    "text": self.documents[i],
                })
        return results

    # ─── Index Persistence ─────────────────────────────────────

    def _save_index(self) -> None:
        """Persist index, metadata, and BM25 state to disk."""
        if self.faiss_index is not None:
            faiss.write_index(
                self.faiss_index,
                os.path.join(self.storage_path, "index.faiss"),
            )

        meta_path = os.path.join(self.storage_path, "metadata.pkl")
        with open(meta_path, "wb") as f:
            pickle.dump({
                "documents": self.documents,
                "metadata": self.metadata,
                "document_index": self.document_index,
                "page_index": self.page_index,
                "embedding_model": self.embedding_model_name,
                "dimension": self.dimension,
                "bm25_weight": self.bm25_weight,
                "dense_weight": self.dense_weight,
                "timestamp": datetime.now().isoformat(),
            }, f)

        # Save page references as JSON for readability
        ref_path = os.path.join(self.storage_path, "page_references.json")
        with open(ref_path, "w") as f:
            json.dump(self.page_references, f, indent=2, default=str)

        print(f"💾 Index saved to {self.storage_path}")

    def _load_index(self) -> bool:
        """Load index, metadata, and BM25 from disk."""
        index_path = os.path.join(self.storage_path, "index.faiss")
        meta_path = os.path.join(self.storage_path, "metadata.pkl")

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            return False

        try:
            self.faiss_index = faiss.read_index(index_path)
            self.dimension = self.faiss_index.d

            with open(meta_path, "rb") as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.metadata = data["metadata"]
                self.document_index = data.get("document_index", [])
                self.page_index = data.get("page_index", {})
                self.embedding_model_name = data.get("embedding_model", "all-MiniLM-L6-v2")
                self.bm25_weight = data.get("bm25_weight", 0.4)
                self.dense_weight = data.get("dense_weight", 0.6)

            # Rebuild BM25 from stored tokenized docs
            if self.document_index:
                self.bm25 = BM25Okapi(self.document_index)

            return True
        except Exception as e:
            print(f"⚠️ Error loading index: {e}")
            return False

    # ─── Page Reference Builder ────────────────────────────────

    def _build_page_index(self, metadata_list: List[Dict]) -> None:
        """Build page-level reference index for citation."""
        self.page_references = {}
        for i, meta in enumerate(metadata_list):
            source = meta.get("source", "unknown")
            page = meta.get("page", 0)
            if source not in self.page_references:
                self.page_references[source] = {}
            if page not in self.page_references[source]:
                self.page_references[source][page] = []
            self.page_references[source][page].append(i)

    # ─── Utility ───────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Return index statistics."""
        loaded = self._load_index() or self.faiss_index is not None
        unique_sources = len(self.page_index) if self.page_index else 0

        return {
            "index_loaded": loaded,
            "total_chunks": len(self.documents),
            "unique_sources": unique_sources,
            "embedding_dimension": self.dimension,
            "embedding_model": self.embedding_model_name,
            "bm25_weight": self.bm25_weight,
            "dense_weight": self.dense_weight,
            "storage_path": self.storage_path,
            "sources": list(self.page_index.keys())[:20] if self.page_index else [],
        }

    def clear_index(self) -> bool:
        """Remove all indexed data from disk."""
        try:
            paths = [
                os.path.join(self.storage_path, "index.faiss"),
                os.path.join(self.storage_path, "metadata.pkl"),
                os.path.join(self.storage_path, "page_references.json"),
            ]
            for p in paths:
                if os.path.exists(p):
                    os.remove(p)

            self.faiss_index = None
            self.bm25 = None
            self.documents = []
            self.metadata = []
            self.document_index = []
            self.page_index = {}
            self.page_references = {}
            return True
        except Exception as e:
            print(f"⚠️ Error clearing index: {e}")
            return False

    def set_weights(self, bm25_weight: float, dense_weight: float) -> None:
        """
        Adjust hybrid ranking weights.

        Args:
            bm25_weight: BM25 keyword weight (0.0 - 1.0)
            dense_weight: Dense semantic weight (0.0 - 1.0)
        """
        total = bm25_weight + dense_weight
        self.bm25_weight = bm25_weight / total
        self.dense_weight = dense_weight / total
        print(f"⚖️ Hybrid weights: BM25={self.bm25_weight:.2f}, Dense={self.dense_weight:.2f}")