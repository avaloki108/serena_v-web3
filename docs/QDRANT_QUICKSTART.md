# Qdrant Integration Quick Start

This guide provides a quick reference for using Qdrant vector database integration in Serena.

## Prerequisites

1. **Docker with Qdrant**:
   ```bash
   docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```

2. **Ollama with embedding model**:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull qwen3-embedding:4b
   ```

## Quick Commands

### 1. Create/Register a Project

```bash
# Generate project configuration (includes Qdrant config)
serena project generate-yml /path/to/your/project

# Or let Serena auto-detect when you first use the project
serena project index /path/to/your/project
```

### 2. Index Your Project

```bash
# This indexes both LSP symbols AND Qdrant vectors
serena project index /path/to/your/project
```

### 3. Search Your Code

```bash
# Semantic search using natural language
serena project search "authentication logic with JWT" /path/to/your/project

# Search for specific patterns
serena project search "database query with SQL injection risk" /path/to/your/project

# Limit results
serena project search "API endpoint handlers" /path/to/your/project --limit 5
```

## Configuration

Edit `.serena/project.yml` in your project:

```yaml
# Default Qdrant configuration (auto-added)
qdrant_config:
  qdrant_url: http://localhost:6333
  ollama_provider_url: http://localhost:11434
  embedding_model: qwen3-embedding:4b
  model_dimension: 2560
  search_score_threshold: 0.80
  max_search_results: 20
  enable_auto_indexing: true
```

### Disable Qdrant

Set `enable_auto_indexing: false` or remove the `qdrant_config` section.

### Use Different Embedding Model

```yaml
qdrant_config:
  embedding_model: "nomic-embed-text:latest"
  model_dimension: 768  # Must match model dimension
```

## Python API Usage

```python
from serena.project import Project
from serena.project_indexer import ProjectIndexer

# Load project
project = Project.load("/path/to/project")

# Create indexer
indexer = ProjectIndexer(project)

# Index files
indexer.index_project_files()

# Search
results = indexer.search_in_project("authentication code", limit=10)

for result in results:
    print(f"File: {result['payload']['file_path']}")
    print(f"Score: {result['score']:.3f}")
    print(f"Preview: {result['payload']['text'][:100]}...")
```

## Common Use Cases

### 1. Find Security Vulnerabilities
```bash
serena project search "SQL injection or XSS vulnerability"
```

### 2. Locate Authentication Code
```bash
serena project search "user authentication and session management"
```

### 3. Find API Endpoints
```bash
serena project search "REST API endpoint definitions"
```

### 4. Search for Similar Code
```bash
serena project search "async function that processes payments"
```

## Troubleshooting

### Qdrant not running
```bash
# Check if running
curl http://localhost:6333/healthz

# Start manually
docker start qdrant

# View logs
docker logs qdrant
```

### Ollama not responding
```bash
# Check if running
curl http://localhost:11434/api/version

# List models
ollama list

# Pull model if missing
ollama pull qwen3-embedding:4b
```

### Index not working
```bash
# Check project config
cat /path/to/project/.serena/project.yml

# Re-index with verbose output
serena project index /path/to/project --log-level INFO
```

## Performance Tips

- **Large projects**: Reduce `batch_size` in config (default: 100)
- **Faster indexing**: Use a smaller embedding model
- **Better results**: Lower `search_score_threshold` (e.g., 0.70)
- **More results**: Increase `max_search_results`

## Advanced Features

### Custom Collection Name
The collection is automatically named `serena_project_<project_name>`. To customize:

```python
from serena.qdrant_client import QdrantClient
from serena.config.web3_config import QdrantConfig

config = QdrantConfig(collection_name_prefix="myapp")
client = QdrantClient(config)
# Collection will be: myapp_<project_name>
```

### Manual Docker Management
Disable auto-start:

```yaml
qdrant_config:
  enable_auto_start: false
```

### Hybrid Search (Coming Soon)
Future versions will support combining vector search with keyword search.

## Resources

- [Full Documentation](./QDRANT_INTEGRATION.md)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Ollama Docs](https://ollama.ai/)
