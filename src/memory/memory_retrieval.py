import yaml
import time
import numpy as np
from typing import List, Dict, Any, Union
from loguru import logger
import os

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    logger.warning("sentence-transformers not installed. Vector retrieval will not work.")
    SentenceTransformer = None

class MemoryRetrieval:
    def __init__(self, config_path: str = "src/config/memory_config.yaml"):
        self.config = self._load_config(config_path)
        self.model = None
        self._initialize_model()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load memory config: {e}")
            return {}

    def _initialize_model(self):
        if SentenceTransformer:
            try:
                model_name = self.config.get('memory', {}).get('retrieval', {}).get('model_name', 'all-MiniLM-L6-v2')
                logger.info(f"Loading embedding model: {model_name}...")
                self.model = SentenceTransformer(model_name)
                logger.info("Embedding model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer model: {e}")
                self.model = None
        else:
            self.model = None

    def get_embedding(self, text: str) -> Union[np.ndarray, None]:
        """Generate embedding for text."""
        if not self.model:
            return None
        try:
            return self.model.encode(text, convert_to_tensor=True)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def calculate_similarity(self, embedding1, embedding2) -> float:
        """Calculate cosine similarity between two embeddings."""
        if not self.model or embedding1 is None or embedding2 is None:
            return 0.0
        try:
            return util.cos_sim(embedding1, embedding2).item()
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def apply_time_decay(self, similarity_score: float, timestamp: float, days_factor: float = 0.01) -> float:
        """
        Apply time decay to similarity score.
        score = score * (1 / (1 + decay_rate * days_passed))
        """
        current_time = time.time()
        days_passed = (current_time - timestamp) / (24 * 3600)
        
        # Avoid negative time if system clock skews
        days_passed = max(0, days_passed)
        
        # Simple decay formula
        decayed_score = similarity_score * (1 / (1 + days_factor * days_passed))
        return decayed_score

    def retrieve_top_k(self, query_text: str, memories: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top K memories based on semantic similarity.
        memories list should contain dicts with 'content' and 'embedding' keys.
        """
        if not self.model or not memories:
            return []

        query_embedding = self.get_embedding(query_text)
        if query_embedding is None:
            return []

        scored_memories = []
        for memory in memories:
            mem_embedding = memory.get('embedding')
            if mem_embedding is None:
                # If embedding missing, try to generate on the fly (slower)
                if 'content' in memory:
                   mem_embedding = self.get_embedding(memory['content'])
            
            if mem_embedding is not None:
                score = self.calculate_similarity(query_embedding, mem_embedding)
                
                # Apply time decay if configured (optional optimization)
                # For strictly semantic search, we might not want time decay here, 
                # but 'context' usually favors recent info.
                if 'timestamp' in memory:
                     score = self.apply_time_decay(score, memory['timestamp'])
                
                scored_memories.append((score, memory))

        # Sort by score desc
        scored_memories.sort(key=lambda x: x[0], reverse=True)

        # Return top K
        return [item[1] for item in scored_memories[:top_k]]
