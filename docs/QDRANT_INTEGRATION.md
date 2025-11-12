# Qdrant Vector Database Integration

This document describes the Qdrant vector database integration for Serena projects, which enables semantic code search and intelligent indexing.

## Overview

The Qdrant integration provides automatic project indexing using vector embeddings, allowing for semantic code search across your project files. This is particularly useful for large codebases where traditional text search may not be sufficient.

## Features

- **Automatic Indexing**: Projects are automatically indexed when registered or when running `serena project index`
- **Semantic Search**: Search code using natural language queries
- **Docker Integration**: Automatically starts Qdrant Docker container if not running
- **Ollama Embeddings**: Uses Ollama for generating embeddings with customizable models
- **Configurable**: All settings can be customized per project

## Configuration

### Default Settings

When a project is created or registered, default Qdrant configuration is automatically added with these settings:

```yaml
qdrant_config:
  qdrant_url: http://localhost:6333
  collection_name_prefix: serena_project
  ollama_provider_url: http://localhost:11434
  embedding_model: qwen3-embedding:4b
  model_dimension: 2560
  search_score_threshold: 0.80
  max_search_results: 20
  docker_container_name: qdrant
  enable_auto_start: true
  batch_size: 100
  enable_auto_indexing: true
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `qdrant_url` | URL of the Qdrant server | `http://localhost:6333` |
| `collection_name_prefix` | Prefix for collection names | `serena_project` |
| `ollama_provider_url` | Ollama API endpoint for embeddings | `http://localhost:11434` |
| `embedding_model` | Model to use for embeddings | `qwen3-embedding:4b` |
| `model_dimension` | Dimension of the embedding vectors | `2560` |
| `search_score_threshold` | Minimum similarity score for search results | `0.80` |
| `max_search_results` | Maximum number of search results to return | `20` |
| `docker_container_name` | Name of the Qdrant Docker container | `qdrant` |
| `enable_auto_start` | Automatically start Qdrant if not running | `true` |
| `batch_size` | Number of documents to index per batch | `100` |
| `enable_auto_indexing` | Automatically index project on registration | `true` |

### Customizing Configuration

Edit your project's `.serena/project.yml` file to customize Qdrant settings:

```yaml
qdrant_config:
  embedding_model: "nomic-embed-text:latest"  # Use a different model
  model_dimension: 768                         # Match the model's dimension
  search_score_threshold: 0.75                # Lower threshold for more results
  max_search_results: 50                      # Return more results
```

## Prerequisites

### 1. Docker

Ensure Docker is installed and running:

```bash
docker --version
```

### 2. Qdrant Docker Container

The integration will automatically start Qdrant if configured, or you can start it manually:

```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

Verify Qdrant is running:

```bash
curl http://localhost:6333/healthz
```

### 3. Ollama

Install Ollama and pull the embedding model:

```bash
# Install Ollama (see https://ollama.ai for installation)
ollama pull qwen3-embedding:4b
```

Verify Ollama is running:

```bash
curl http://localhost:11434/api/version
```

## Usage

### Automatic Indexing

When you create a new project or run the index command, Qdrant indexing happens automatically:

```bash
# Generate project configuration (includes Qdrant config)
serena project generate-yml /path/to/project

# Index the project (includes Qdrant indexing)
serena project index /path/to/project
```

### Manual Indexing with Python API

```python
from serena.project import Project
from serena.project_indexer import ProjectIndexer

# Load project
project = Project.load("/path/to/project")

# Create indexer
indexer = ProjectIndexer(project)

# Index all files
indexer.index_project_files()

# Search for code
results = indexer.search_in_project("authentication logic")
for result in results:
    print(f"Score: {result['score']}")
    print(f"File: {result['payload']['file_path']}")
    print(f"Content: {result['payload']['text'][:100]}...")
```

### Disabling Qdrant Indexing

To disable automatic Qdrant indexing for a project, edit `.serena/project.yml`:

```yaml
qdrant_config:
  enable_auto_indexing: false
```

Or remove the `qdrant_config` section entirely.

## Architecture

### Components

1. **QdrantConfig** (`src/serena/config/web3_config.py`): Configuration dataclass for Qdrant settings
2. **QdrantClient** (`src/serena/qdrant_client.py`): Low-level client for interacting with Qdrant API
3. **ProjectIndexer** (`src/serena/project_indexer.py`): High-level interface for indexing projects

### Indexing Flow

1. Project files are gathered using `project.gather_source_files()`
2. Each file is read and prepared as a document with metadata
3. Documents are sent to Ollama for embedding generation
4. Embeddings are stored in Qdrant with file path and content as payload
5. Collection is named based on project name (e.g., `serena_project_myproject`)

### Search Flow

1. Query text is sent to Ollama for embedding generation
2. Vector similarity search is performed in Qdrant
3. Results above the score threshold are returned
4. Results include score, file path, and content

## Troubleshooting

### Qdrant Not Starting

If Qdrant fails to start automatically:

1. Check Docker is running: `docker ps`
2. Start Qdrant manually: `docker start qdrant`
3. Check logs: `docker logs qdrant`

### Ollama Connection Issues

If embedding generation fails:

1. Verify Ollama is running: `curl http://localhost:11434/api/version`
2. Check the model is installed: `ollama list`
3. Pull the model if needed: `ollama pull qwen3-embedding:4b`

### High Memory Usage

For large projects, consider:

1. Reducing `batch_size` in configuration
2. Using a smaller embedding model
3. Increasing available memory for Docker

## Performance Considerations

- **Indexing Time**: Depends on project size and embedding model speed
- **Storage**: Each file requires storage for embeddings (~10KB per file for 2560 dimensions)
- **Search Speed**: Vector search is fast (typically <100ms for collections up to 100K vectors)

## Examples

### Example: Searching for Security Vulnerabilities

```python
from serena.project_indexer import ProjectIndexer
from serena.project import Project

project = Project.load("/path/to/web3/project")
indexer = ProjectIndexer(project)

# Search for potential security issues
results = indexer.search_in_project(
    "SQL injection vulnerability or unsafe user input",
    limit=10
)

for result in results:
    print(f"\n{result['payload']['file_path']} (Score: {result['score']:.3f})")
    print(result['payload']['text'][:200])
```

### Example: Finding Similar Code

```python
# Find code similar to a specific pattern
results = indexer.search_in_project(
    "async function that handles authentication with JWT tokens"
)
```

## Future Enhancements

- Support for hybrid search (combining vector and keyword search)
- Incremental indexing (only index changed files)
- Multiple embedding models for different file types
- Integration with code review and security scanning tools

## References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://ollama.ai/)
- [Vector Search Basics](https://www.pinecone.io/learn/vector-search/)
