import json
import os
import time
import uuid
from typing import List, Dict, Any, Optional
from loguru import logger
from .memory_retrieval import MemoryRetrieval

class MemoryManager:
    def __init__(self, config_path: str = "src/config/memory_config.yaml", storage_dir: str = "data/memory"):
        self.retriever = MemoryRetrieval(config_path)
        self.storage_dir = storage_dir
        self.config = self.retriever.config
        
        self.short_term_memory: List[Dict] = []
        self.long_term_memory: List[Dict] = []
        self.episodic_memory: List[Dict] = []
        
        self._ensure_storage_dir()
        self._load_memories()

    def _ensure_storage_dir(self):
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_file_path(self, filename: str) -> str:
        return os.path.join(self.storage_dir, filename)

    def add_memory(self, content: str, memory_type: str = "short_term", importance: int = 0, metadata: Dict = None) -> str:
        """
        Add a new memory to the system.
        """
        memory_id = str(uuid.uuid4())
        timestamp = time.time()
        
        embedding = self.retriever.get_embedding(content)
        
        memory_data = {
            "id": memory_id,
            "content": content,
            "type": memory_type,
            "importance": importance,
            "timestamp": timestamp,
            "metadata": metadata or {},
            # 注意: embedding 需要能在内存中用于计算，但在 JSON 序列化时通常不保存或需要特殊处理
            # 这里我们在内存中保存 embedding 对象，save 时忽略或转存
            "embedding": embedding 
        }

        if memory_type == "short_term":
            self.short_term_memory.append(memory_data)
        elif memory_type == "long_term":
            self.long_term_memory.append(memory_data)
        elif memory_type == "episodic":
            self.episodic_memory.append(memory_data)
        else:
            logger.warning(f"Unknown memory type: {memory_type}, adding to short_term")
            self.short_term_memory.append(memory_data)
            
        logger.info(f"Added {memory_type} memory: {content[:50]}... (Importance: {importance})")
        self._save_memories() # Simple auto-save for now
        return memory_id

    def retrieve_similar(self, current_context: str, top_k: int = 5, memory_type: str = None) -> List[Dict]:
        """
        Retrieve relevant memories.
        """
        target_memories = []
        if memory_type == "short_term":
            target_memories = self.short_term_memory
        elif memory_type == "long_term":
            target_memories = self.long_term_memory
        elif memory_type == "episodic":
            target_memories = self.episodic_memory
        else:
            # If type not specified, search all
            target_memories = self.short_term_memory + self.long_term_memory + self.episodic_memory

        return self.retriever.retrieve_top_k(current_context, target_memories, top_k)

    def calculate_importance(self, memory_data: Dict) -> int:
        """
        Calculate importance score based on rules defined in config.
        Expected keys in memory_data['metadata']: 
            - pnl_percentage (float)
            - volatility_ratio (float)
            - ai_consensus (str) ["split", "agree"]
        """
        score = 0
        weights = self.config.get('memory', {}).get('importance_weights', {})
        metadata = memory_data.get('metadata', {})
        
        pnl_pct = abs(float(metadata.get('pnl_percentage', 0)))
        volatility = float(metadata.get('volatility_ratio', 1.0))
        consensus = metadata.get('ai_consensus', 'agree')
        
        # Profit/Loss logic
        if pnl_pct >= 10:
             score = max(score, weights.get('profit_high', 85))
        elif pnl_pct >= 5: # Assuming >5% loss is explicitly handled or just treated as high impact
             # User prompt said "loss > 5%: high score", here generic PnL magnitude check
             score = max(score, weights.get('profit_loss', 80))
             
        # Volatility
        if volatility >= 2.0:
            score = max(score, weights.get('volatility_high', 70))
            
        # Consensus
        if consensus == 'split':
             score = max(score, weights.get('consensus_split', 60))
             
        return min(100, score)

    def cleanup_old_memories(self):
        """
        Cleanup memories based on retention policy and importance.
        """
        current_time = time.time()
        retention_config = self.config.get('memory', {}).get('retention', {})
        cleanup_thresholds = self.config.get('memory', {}).get('cleanup', {})
        
        blobs = [
            (self.short_term_memory, retention_config.get('short_term', 1)),
            # Long term logic is more complex based on importance, handled below explicitly if needed
            # For simplicity, treating long_term list iteration separately
        ]

        # 1. Cleanup Short Term (Strict time limit)
        st_days = retention_config.get('short_term', 1)
        self.short_term_memory = [
            m for m in self.short_term_memory 
            if (current_time - m['timestamp']) < (st_days * 86400)
        ]
        
        # 2. Cleanup Long Term (Based on Importance)
        min_days = retention_config.get('long_term_min', 30)
        med_days = retention_config.get('long_term_med', 90)
        high_days = retention_config.get('long_term_high', 180)
        
        low_thresh = cleanup_thresholds.get('low_importance_threshold', 20)
        med_thresh = cleanup_thresholds.get('medium_importance_threshold', 50)
        high_thresh = cleanup_thresholds.get('high_importance_threshold', 80)
        
        new_long_term = []
        for m in self.long_term_memory:
            age_days = (current_time - m['timestamp']) / 86400
            imp = m['importance']
            
            keep = True
            if imp < low_thresh and age_days > min_days:
                keep = False
            elif imp < med_thresh and age_days > med_days:
                keep = False
            elif imp < high_thresh and age_days > high_days:
                keep = False
            # imp >= high_thresh -> keep forever (implicit)
            
            if keep:
                new_long_term.append(m)
                
        self.long_term_memory = new_long_term
        
        self._save_memories()
        logger.info("Memory cleanup completed.")

    def _save_memories(self):
        # Exclude embedding objects from JSON
        def clean_for_dump(mem_list):
            dumps = []
            for m in mem_list:
                copy_m = m.copy()
                if 'embedding' in copy_m:
                    del copy_m['embedding']
                dumps.append(copy_m)
            return dumps

        data = {
            "short_term": clean_for_dump(self.short_term_memory),
            "long_term": clean_for_dump(self.long_term_memory),
            "episodic": clean_for_dump(self.episodic_memory)
        }
        
        try:
            with open(self._get_file_path("memories.json"), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memories: {e}")

    def _load_memories(self):
        path = self._get_file_path("memories.json")
        if not os.path.exists(path):
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.short_term_memory = data.get("short_term", [])
            self.long_term_memory = data.get("long_term", [])
            self.episodic_memory = data.get("episodic", [])
            
            # Re-generate embeddings (expensive!) or load cached separate embedding file
            # For this MVP, we re-generate on load if content exists, or do lazy loading.
            # To avoid slow startup, we'll do it lazily or assume retriever handles missing embeddings gracefully
            # (which my retrieve_similar implementation does check)
            
            logger.info(f"Loaded {len(self.short_term_memory)} short-term, {len(self.long_term_memory)} long-term memories.")
            
        except Exception as e:
            logger.error(f"Failed to load memories: {e}")
