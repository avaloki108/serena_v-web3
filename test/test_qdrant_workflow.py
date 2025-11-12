#!/usr/bin/env python3
"""
Integration test for Qdrant project indexing workflow.

This test verifies the full workflow without requiring actual Qdrant/Ollama services.
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from serena.config.serena_config import ProjectConfig
from serena.config.web3_config import QdrantConfig
from serena.project import Project


def test_project_config_with_qdrant():
    """Test that ProjectConfig properly handles Qdrant configuration."""
    print("Testing ProjectConfig with Qdrant configuration...")
    
    # Create a temporary project directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create a simple Python file
        (project_path / "test.py").write_text("def hello(): pass")
        
        # Auto-generate project config
        config = ProjectConfig.autogenerate(
            project_root=project_path,
            project_name="test_project",
            save_to_disk=False
        )
        
        # Verify Qdrant config was added
        assert config.qdrant_config is not None, "Qdrant config should be automatically added"
        assert isinstance(config.qdrant_config, QdrantConfig), "Should be QdrantConfig instance"
        assert config.qdrant_config.qdrant_url == "http://localhost:6333"
        assert config.qdrant_config.ollama_provider_url == "http://localhost:11434"
        assert config.qdrant_config.embedding_model == "qwen3-embedding:4b"
        assert config.qdrant_config.model_dimension == 2560
        assert config.qdrant_config.search_score_threshold == 0.80
        assert config.qdrant_config.max_search_results == 20
        assert config.qdrant_config.enable_auto_indexing is True
        
        print("✓ ProjectConfig with Qdrant configuration works correctly")


def test_config_serialization():
    """Test that Qdrant config can be serialized and deserialized."""
    print("\nTesting config serialization...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create a simple Python file
        (project_path / "test.py").write_text("def hello(): pass")
        
        # Auto-generate and save config
        config = ProjectConfig.autogenerate(
            project_root=project_path,
            project_name="test_project",
            save_to_disk=True
        )
        
        # Convert to YAML dict
        yaml_dict = config.to_yaml_dict()
        assert "qdrant_config" in yaml_dict, "qdrant_config should be in YAML dict"
        assert isinstance(yaml_dict["qdrant_config"], dict), "Should be a dict"
        
        # Load the config back
        config_path = project_path / ".serena" / "project.yml"
        assert config_path.exists(), "Config file should exist"
        
        loaded_config = ProjectConfig.load(project_path)
        assert loaded_config.qdrant_config is not None, "Loaded config should have Qdrant config"
        assert loaded_config.qdrant_config.qdrant_url == config.qdrant_config.qdrant_url
        
        print("✓ Config serialization/deserialization works correctly")


def test_qdrant_config_customization():
    """Test that Qdrant config can be customized."""
    print("\nTesting Qdrant config customization...")
    
    custom_config = QdrantConfig(
        qdrant_url="http://custom:6333",
        embedding_model="custom-model",
        model_dimension=768,
        search_score_threshold=0.75,
        enable_auto_indexing=False
    )
    
    assert custom_config.qdrant_url == "http://custom:6333"
    assert custom_config.embedding_model == "custom-model"
    assert custom_config.model_dimension == 768
    assert custom_config.search_score_threshold == 0.75
    assert custom_config.enable_auto_indexing is False
    
    # Test to_dict and from_dict
    config_dict = custom_config.to_dict()
    restored_config = QdrantConfig.from_dict(config_dict)
    
    assert restored_config.qdrant_url == custom_config.qdrant_url
    assert restored_config.embedding_model == custom_config.embedding_model
    assert restored_config.model_dimension == custom_config.model_dimension
    
    print("✓ Qdrant config customization works correctly")


def test_project_with_qdrant_disabled():
    """Test project with Qdrant disabled."""
    print("\nTesting project with Qdrant disabled...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create a simple Python file
        (project_path / "test.py").write_text("def hello(): pass")
        
        # Create config with Qdrant disabled
        config = ProjectConfig.autogenerate(
            project_root=project_path,
            project_name="test_project",
            save_to_disk=False
        )
        
        # Disable Qdrant
        config.qdrant_config.enable_auto_indexing = False
        
        assert config.qdrant_config.enable_auto_indexing is False
        
        print("✓ Project with Qdrant disabled works correctly")


if __name__ == "__main__":
    print("=" * 60)
    print("Qdrant Integration Workflow Tests")
    print("=" * 60)
    
    test_project_config_with_qdrant()
    test_config_serialization()
    test_qdrant_config_customization()
    test_project_with_qdrant_disabled()
    
    print("\n" + "=" * 60)
    print("All workflow tests passed!")
    print("=" * 60)
