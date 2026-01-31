import pytest
import time
import os
import shutil
from src.memory.memory_system import MemoryManager

# 配置测试用的存储目录
TEST_STORAGE_DIR = "tests/data/memory"
TEST_CONFIG_PATH = "src/config/memory_config.yaml"

@pytest.fixture
def memory_manager():
    # Setup
    if os.path.exists(TEST_STORAGE_DIR):
        shutil.rmtree(TEST_STORAGE_DIR)
    
    manager = MemoryManager(config_path=TEST_CONFIG_PATH, storage_dir=TEST_STORAGE_DIR)
    yield manager
    
    # Teardown
    if os.path.exists(TEST_STORAGE_DIR):
        shutil.rmtree(TEST_STORAGE_DIR)

def test_add_and_retrieve_memory(memory_manager):
    # Test adding short term memory
    content = "Bitcoin price dropped 5% due to regulatory news."
    mid = memory_manager.add_memory(content, memory_type="short_term", importance=80)
    assert mid is not None
    assert len(memory_manager.short_term_memory) == 1
    
    # Test adding long term memory
    content2 = "Always hedge when volatility is above 3.0."
    mid2 = memory_manager.add_memory(content2, memory_type="long_term", importance=90)
    assert len(memory_manager.long_term_memory) == 1
    
    # Test retrieval (semantic)
    # Using a query similar to the second memory
    query = "strategies for high volatility"
    results = memory_manager.retrieve_similar(query, top_k=1)
    
    # Note: If sentence-transformers is missing, this might return empty or low score
    # But if installed, it should match content2
    if memory_manager.retriever.model:
        assert len(results) > 0
        assert results[0]['content'] == content2

def test_importance_calculation(memory_manager):
    # High profit case
    data_high_profit = {"metadata": {"pnl_percentage": 12.0}}
    score = memory_manager.calculate_importance(data_high_profit)
    assert score >= 85
    
    # Volatility case
    data_volatility = {"metadata": {"volatility_ratio": 2.5}}
    score = memory_manager.calculate_importance(data_volatility)
    assert score >= 70

def test_cleanup_logic(memory_manager):
    # Mocking time logic is hard without patching time.time, 
    # instead we will manually modify timestamps of memories
    
    # 1. Add old low importance memory (Short Term) - Should be deleted (retention 1 day)
    mid1 = memory_manager.add_memory("Old news", "short_term", 10)
    memory_manager.short_term_memory[0]['timestamp'] = time.time() - (2 * 86400) # 2 days ago
    
    # 2. Add old low importance memory (Long Term) - Should be deleted (min retention 30 days, imp < 20)
    mid2 = memory_manager.add_memory("Old strategy", "long_term", 10)
    memory_manager.long_term_memory[0]['timestamp'] = time.time() - (31 * 86400) # 31 days ago
    
    # 3. Add old high importance memory - Should KEEP
    mid3 = memory_manager.add_memory("Golden rule", "long_term", 90)
    memory_manager.long_term_memory[1]['timestamp'] = time.time() - (100 * 86400) # 100 days ago
    
    memory_manager.cleanup_old_memories()
    
    # Check Short Term
    assert len(memory_manager.short_term_memory) == 0
    
    # Check Long Term
    # mid2 should be gone, mid3 should allow stay
    long_term_ids = [m['id'] for m in memory_manager.long_term_memory]
    assert mid2 not in long_term_ids  # Should be deleted
    # Fix: logic for add_memory appends, so indices might shift. Checking by ID logic is safer.
    # mid3 importance 90 > high_thresh 80 -> keep forever
    found_mid3 = any(m['content'] == "Golden rule" for m in memory_manager.long_term_memory)
    assert found_mid3

def test_persistence(memory_manager):
    memory_manager.add_memory("Test persistence", "short_term", 50)
    
    # Re-instantiate manager
    new_manager = MemoryManager(config_path=TEST_CONFIG_PATH, storage_dir=TEST_STORAGE_DIR)
    assert len(new_manager.short_term_memory) == 1
    assert new_manager.short_term_memory[0]['content'] == "Test persistence"
