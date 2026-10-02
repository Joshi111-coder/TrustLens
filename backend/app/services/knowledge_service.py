import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.config import settings

class KnowledgeBaseInterface(ABC):
    """
    Abstract interface for TrustLens knowledge retrieval.
    Enables swapping Local JSON with FAISS, ChromaDB, or pgvector
    without rewriting application logic.
    """
    
    @abstractmethod
    def search(self, query: str, limit: int = 5, keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def get_by_id(self, source_id: str) -> Optional[Dict[str, Any]]:
        pass


class LocalJSONKnowledgeBase(KnowledgeBaseInterface):
    """
    Local in-memory keyword & pattern knowledge base.
    Loads structured official guidance from trusted_sources.json.
    """
    
    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or (settings.DATA_DIR / "trusted_sources.json")
        self.sources: List[Dict[str, Any]] = []
        self._load()
        
    def _load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.sources = json.load(f)
            except Exception as e:
                print(f"[KnowledgeBase] Error loading sources from {self.file_path}: {e}")
                self.sources = []
        else:
            print(f"[KnowledgeBase] File not found: {self.file_path}")
            self.sources = []
            
    def search(self, query: str, limit: int = 5, keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if not self.sources:
            return []
            
        q_lower = query.lower()
        scored_sources = []
        
        for item in self.sources:
            score = 0
            item_keywords = [k.lower() for k in item.get("keywords", [])]
            topic_lower = item.get("topic", "").lower()
            name_lower = item.get("name", "").lower()
            summary_lower = item.get("summary", "").lower()
            
            # Check explicit detected keywords
            if keywords:
                for kw in keywords:
                    kw_l = kw.lower()
                    if any(kw_l in ik or ik in kw_l for ik in item_keywords):
                        score += 3
                        
            # Check against query text
            for ik in item_keywords:
                if ik in q_lower:
                    score += 2
                    
            if topic_lower in q_lower:
                score += 2
            if name_lower in q_lower:
                score += 2
            for word in q_lower.split():
                if len(word) > 3 and word in summary_lower:
                    score += 0.5
                    
            if score > 0:
                scored_sources.append((score, item))
                
        # Sort by relevance score descending
        scored_sources.sort(key=lambda x: x[0], reverse=True)
        results = [item for _, item in scored_sources[:limit]]
        
        # If no specific matches found, return default educational sources (SEBI & RBI)
        if not results and self.sources:
            results = self.sources[:3]
            
        return results

    def get_by_id(self, source_id: str) -> Optional[Dict[str, Any]]:
        for item in self.sources:
            if item.get("id") == source_id:
                return item
        return None


class VectorKnowledgeBasePlaceholder(KnowledgeBaseInterface):
    """
    RAG / Vector Database Adapter placeholder (FAISS / ChromaDB / Milvus).
    Developers can initialize this adapter with an embedding model
    and vector store index when scaling.
    """
    def __init__(self, collection_name: str = "trustlens_sources"):
        self.collection_name = collection_name
        
    def search(self, query: str, limit: int = 5, keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        # In future: query vector database using embedding similarity
        raise NotImplementedError("Vector DB extension can be enabled in Phase 2.")

    def get_by_id(self, source_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("Vector DB extension can be enabled in Phase 2.")


# Singleton instance of current Knowledge Base
knowledge_base: KnowledgeBaseInterface = LocalJSONKnowledgeBase()

