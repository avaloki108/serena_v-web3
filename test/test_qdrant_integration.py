#!/usr/bin/env python3
"""
Test script for Qdrant integration.
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from serena.config.web3_config import QdrantConfig
from serena.qdrant_client import QdrantClient


def test_qdrant_config():
    """Test QdrantConfig creation and serialization."""
    print("Testing QdrantConfig...")
    config = QdrantConfig()
    
    # Test defaults
    assert config.qdrant_url == "http://localhost:6333"
    assert config.ollama_provider_url == "http://localhost:11434"
    assert config.embedding_model == "qwen3-embedding:4b"
    assert config.model_dimension == 2560
    assert config.search_score_threshold == 0.80
    assert config.max_search_results == 20
    
    # Test serialization
    config_dict = config.to_dict()
    assert config_dict["qdrant_url"] == "http://localhost:6333"
    
    # Test deserialization
    config2 = QdrantConfig.from_dict(config_dict)
    assert config2.qdrant_url == config.qdrant_url
    
    print("✓ QdrantConfig tests passed")


def test_qdrant_client_basic():
    """Test QdrantClient basic functionality."""
    print("\nTesting QdrantClient (basic)...")
    config = QdrantConfig(enable_auto_start=False)
    
    try:
        client = QdrantClient(config)
        print(f"✓ QdrantClient created (Qdrant running: {client.is_qdrant_running()})")
    except Exception as e:
        print(f"⚠ QdrantClient creation failed (expected if Qdrant not running): {e}")


def test_collection_name_sanitization():
    """Test collection name generation."""
    print("\nTesting collection name sanitization...")
    config = QdrantConfig(enable_auto_start=False)
    
    try:
        client = QdrantClient(config)
    except Exception:
        # Create client without checking if Qdrant is running
        config.enable_auto_start = False
        client = QdrantClient.__new__(QdrantClient)
        client.config = config
    
    # Test various project names
    assert client.get_collection_name("my-project") == "serena_project_my_project"
    assert client.get_collection_name("My Project") == "serena_project_my_project"
    assert client.get_collection_name("test_123") == "serena_project_test_123"
    
    print("✓ Collection name sanitization tests passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Qdrant Integration Test Suite")
    print("=" * 60)
    
    test_qdrant_config()
    test_qdrant_client_basic()
    test_collection_name_sanitization()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
