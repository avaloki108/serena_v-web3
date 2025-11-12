#!/usr/bin/env python3
"""
Code verification script - checks syntax and structure without importing.
"""

import ast
import sys
from pathlib import Path


def check_python_syntax(file_path):
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path, 'r') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)


def verify_qdrant_files():
    """Verify all Qdrant-related files have valid syntax."""
    print("=" * 60)
    print("Qdrant Integration Code Verification")
    print("=" * 60)
    
    repo_root = Path(__file__).parent.parent
    
    files_to_check = [
        "src/serena/qdrant_client.py",
        "src/serena/project_indexer.py",
        "src/serena/config/web3_config.py",
        "src/serena/config/serena_config.py",
        "src/serena/cli.py",
        "test/test_qdrant_integration.py",
        "test/test_qdrant_workflow.py",
        "examples/qdrant_demo.py",
    ]
    
    all_valid = True
    for file_path in files_to_check:
        full_path = repo_root / file_path
        if not full_path.exists():
            print(f"✗ {file_path} - FILE NOT FOUND")
            all_valid = False
            continue
            
        valid, error = check_python_syntax(full_path)
        if valid:
            print(f"✓ {file_path} - Valid syntax")
        else:
            print(f"✗ {file_path} - Syntax error: {error}")
            all_valid = False
    
    print("\n" + "=" * 60)
    if all_valid:
        print("All files have valid Python syntax!")
        print("=" * 60)
        return 0
    else:
        print("Some files have errors!")
        print("=" * 60)
        return 1


def check_key_components():
    """Check that key components are present in the code."""
    print("\nChecking key components...")
    
    repo_root = Path(__file__).parent.parent
    
    # Check QdrantConfig exists
    web3_config = (repo_root / "src/serena/config/web3_config.py").read_text()
    if "class QdrantConfig" in web3_config:
        print("✓ QdrantConfig class found")
    else:
        print("✗ QdrantConfig class not found")
    
    # Check QdrantClient exists
    qdrant_client = (repo_root / "src/serena/qdrant_client.py").read_text()
    if "class QdrantClient" in qdrant_client:
        print("✓ QdrantClient class found")
    else:
        print("✗ QdrantClient class not found")
    
    # Check ProjectIndexer exists
    project_indexer = (repo_root / "src/serena/project_indexer.py").read_text()
    if "class ProjectIndexer" in project_indexer:
        print("✓ ProjectIndexer class found")
    else:
        print("✗ ProjectIndexer class not found")
    
    # Check CLI search command
    cli = (repo_root / "src/serena/cli.py").read_text()
    if 'def search(' in cli:
        print("✓ CLI search command found")
    else:
        print("✗ CLI search command not found")
    
    # Check documentation
    if (repo_root / "docs/QDRANT_INTEGRATION.md").exists():
        print("✓ Qdrant documentation exists")
    else:
        print("✗ Qdrant documentation not found")


if __name__ == "__main__":
    exit_code = verify_qdrant_files()
    check_key_components()
    sys.exit(exit_code)
