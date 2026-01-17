import logging
import time
from config import CONFIG

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        self.config = CONFIG.get("CLEANING", {})
        self.enabled = self.config.get("ENABLED", False)
        
        # Determine Models needed
        self.english_conf = self.config.get("ENGLISH", {})
        self.chinese_conf = self.config.get("CHINESE", {})
        
        self.models = {} # Cache: 'model_name' -> Model Object
        self.util = None
        
        if self.enabled:
            try:
                from sentence_transformers import SentenceTransformer, util
                self.util = util
                self.SentenceTransformer = SentenceTransformer # Class ref
                
                # Pre-load or Lazy-load? Lazy load is better if not cleaning logic runs.
                # But here we usually run cleaning. Let's pre-load unique models.
                unique_models = set([
                    self.english_conf.get("MODEL_NAME", "all-MiniLM-L6-v2"),
                    self.chinese_conf.get("MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
                ])
                
                for m_name in unique_models:
                    if not m_name: continue
                    logger.info(f"Loading Cleaning Model: {m_name}...")
                    self.models[m_name] = self.SentenceTransformer(m_name)
                    
                logger.info("Cleaning Models Loaded Successfully.")
            except ImportError:
                logger.error("sentence-transformers not installed. Cleaning disabled.")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to load cleaning models: {e}")
                self.enabled = False
    
    def _is_valid(self, item) -> bool:
        """
        Check if an item is valid/high-quality enough to be included.
        """
        title = item.get('title', '').strip()
        content = item.get('content', '').strip()
        
        # 1. Check for Empty Fields
        if not title or not content:
            return False
            
        # 2. Check for Generic Titles (Google News artifacts)
        if title.lower() in ["google news", "google", "news"]:
            return False
            
        # 3. Check Content Length
        if len(content) < 50:
            return False
            
        return True

    def clean_data(self, data_map: dict, language: str = "ENGLISH") -> dict:
        """
        Deduplication for a specific language scope.
        data_map: { 'source_name': [item1, ...], ... }
        language: "ENGLISH" or "CHINESE" key in config.
        """
        if not self.enabled:
            return data_map
            
        conf = self.english_conf if language == "ENGLISH" else self.chinese_conf
        model_name = conf.get("MODEL_NAME")
        threshold = conf.get("SIMILARITY_THRESHOLD", 0.85)
        
        model = self.models.get(model_name)
        if not model:
            logger.warning(f"Model {model_name} not loaded. Skipping cleaning.")
            return data_map

        logger.info(f"[{language}] Starting Semantic Deduplication ({model_name})...")
        start_time = time.time()
        
        # 1. Flatten Data
        all_items = []
        references = [] 
        
        for source_key, items in data_map.items():
            for idx, item in enumerate(items):
                # Validation / Quality Check
                if not self._is_valid(item):
                    continue

                text = f"{item.get('title', '')}. {item.get('content', '')[:200]}" 
                all_items.append(text)
                references.append({
                    "key": source_key,
                    "item": item,
                    "is_duplicate": False
                })
        
        if not all_items:
            return data_map

        # 2. Generate Embeddings
        logger.info(f"[{language}] Encoding {len(all_items)} items...")
        embeddings = model.encode(all_items, convert_to_tensor=True)
        
        # 3. Compute & Cluster
        logger.info(f"[{language}] Clustering (Threshold {threshold})...")
        clusters = self.util.community_detection(embeddings, min_community_size=1, threshold=threshold)
        
        duplicates_count = 0
        for cluster in clusters:
            if len(cluster) <= 1: continue
            
            cluster_refs = [references[i] for i in cluster]
            # Strategy: Keep longest content
            cluster_refs.sort(key=lambda x: len(x['item'].get('content', '') or ''), reverse=True)
            
            keeper = cluster_refs[0]
            dropped = cluster_refs[1:]
            
            for d in dropped:
                d['is_duplicate'] = True
                duplicates_count += 1
                
        # 5. Reconstruct
        cleaned_map = {k: [] for k in data_map.keys()}
        for ref in references:
            if not ref['is_duplicate']:
                cleaned_map[ref['key']].append(ref['item'])
                
        elapsed = time.time() - start_time
        logger.info(f"[{language}] Deduplication Complete {elapsed:.2f}s. Removed {duplicates_count} duplicates.")
        
        return cleaned_map
