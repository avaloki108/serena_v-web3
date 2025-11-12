# Qdrant Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Serena Project                          │
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │ Project.py   │────▶│ProjectIndexer│────▶│QdrantClient  │   │
│  └──────────────┘     └──────────────┘     └──────┬───────┘   │
│         │                    │                     │           │
│         │                    │                     │           │
│         ▼                    ▼                     ▼           │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │ ProjectConfig│     │Source Files  │     │Docker Check  │   │
│  │ + Qdrant     │     │Gathering     │     │& Auto-start  │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTP Requests
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                          │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │  Ollama Service  │              │  Qdrant Service  │        │
│  │  localhost:11434 │              │  localhost:6333  │        │
│  │                  │              │                  │        │
│  │  Model:          │              │  Vector Store    │        │
│  │  qwen3-embed:4b  │◀────────────▶│  Collections     │        │
│  │  Dim: 2560       │ Embeddings   │  Similarity      │        │
│  └──────────────────┘              └──────────────────┘        │
│          │                                  │                  │
│          └──────────────┬───────────────────┘                  │
│                         │                                      │
│                  ┌──────▼───────┐                              │
│                  │ Docker Engine│                              │
│                  │ (Qdrant)     │                              │
│                  └──────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. QdrantConfig (`src/serena/config/web3_config.py`)
**Purpose**: Configuration dataclass
- Stores all Qdrant-related settings
- Provides serialization/deserialization
- Integrated into ProjectConfig

**Key Settings**:
- Qdrant URL and connection settings
- Ollama provider URL and model
- Search thresholds and limits
- Docker container name
- Auto-start and auto-indexing flags

### 2. QdrantClient (`src/serena/qdrant_client.py`)
**Purpose**: Low-level Qdrant API client
- Manages connection to Qdrant
- Handles Docker container lifecycle
- Generates embeddings via Ollama
- Performs vector operations (index, search)

**Key Methods**:
- `is_qdrant_running()` - Health check
- `_start_qdrant_docker()` - Docker management
- `generate_embedding(text)` - Ollama integration
- `index_documents(...)` - Batch indexing
- `search(query, ...)` - Vector similarity search

### 3. ProjectIndexer (`src/serena/project_indexer.py`)
**Purpose**: High-level project indexing interface
- Bridges Project and QdrantClient
- Manages indexing workflow
- Provides search interface

**Key Methods**:
- `index_project_files()` - Full project indexing
- `search_in_project(query)` - Semantic search
- `delete_project_index()` - Cleanup

### 4. CLI Integration (`src/serena/cli.py`)
**Purpose**: Command-line interface
- `project generate-yml` - Adds Qdrant config
- `project index` - Triggers indexing
- `project search` - Semantic search command

## Data Flow

### Indexing Flow

```
1. User Command
   serena project index /path/to/project
          │
          ▼
2. CLI (_index_project)
   - Runs LSP indexing (existing)
   - Checks if Qdrant enabled
          │
          ▼
3. ProjectIndexer.index_project_files()
   - Gathers source files
   - Creates documents with metadata
          │
          ▼
4. For each batch of files:
   ┌──────────────────────────┐
   │ File → Text              │
   │ Text → Ollama            │
   │ Ollama → Embedding       │
   │ Embedding → Qdrant       │
   └──────────────────────────┘
          │
          ▼
5. Qdrant Collection
   Collection: serena_project_<name>
   - Vectors (2560 dim)
   - Metadata (path, content)
```

### Search Flow

```
1. User Query
   serena project search "auth logic"
          │
          ▼
2. CLI (search command)
   - Loads project
   - Creates ProjectIndexer
          │
          ▼
3. ProjectIndexer.search_in_project()
   - Sends query to Ollama
   - Gets query embedding
          │
          ▼
4. QdrantClient.search()
   - Vector similarity search
   - Filters by threshold (0.80)
   - Returns top N results (max 20)
          │
          ▼
5. Results Display
   - File path
   - Similarity score
   - Content preview
```

## Docker Management Flow

```
1. QdrantClient.__init__()
          │
          ▼
2. _ensure_qdrant_running()
          │
          ▼
3. is_qdrant_running()?
   GET http://localhost:6333/healthz
          │
    ┌─────┴─────┐
    │           │
   Yes          No
    │           │
    └─────┐     └──▶ enable_auto_start?
          │              │
          │         ┌────┴────┐
          │        Yes        No
          │         │          │
          │         ▼          └──▶ RAISE ERROR
          │   _start_qdrant_docker()
          │         │
          │    ┌────┴────┐
          │    │         │
          │  Exists?    New
          │    │         │
          │    ▼         ▼
          │  docker    docker
          │  start     run -d
          │    │         │
          │    └────┬────┘
          │         │
          ▼         ▼
    Wait for health check
          │
          ▼
     Ready for use
```

## Collection Structure

Each project gets its own collection:

```
Collection: serena_project_<sanitized_project_name>

Vector Configuration:
  - Size: 2560 (qwen3-embedding:4b dimension)
  - Distance: Cosine similarity

Points Structure:
{
  "id": <integer>,
  "vector": [<2560 floats>],
  "payload": {
    "text": "<file content>",
    "file_path": "<relative/path/to/file.py>",
    "absolute_path": "</full/path/to/file.py>",
    "project_name": "<project_name>"
  }
}
```

## Configuration Integration

```
project.yml
├── project_name: "my_project"
├── languages: ["python"]
├── ... (other settings)
└── qdrant_config:
    ├── qdrant_url: "http://localhost:6333"
    ├── ollama_provider_url: "http://localhost:11434"
    ├── embedding_model: "qwen3-embedding:4b"
    ├── model_dimension: 2560
    ├── search_score_threshold: 0.80
    ├── max_search_results: 20
    ├── enable_auto_start: true
    └── enable_auto_indexing: true
```

## Error Handling Strategy

1. **Qdrant Not Running**:
   - If `enable_auto_start: true` → Try to start
   - If `enable_auto_start: false` → Raise error
   - If start fails → Raise error with details

2. **Ollama Not Available**:
   - Raise error with connection details
   - User must start Ollama manually

3. **Indexing Failures**:
   - Log warning for individual files
   - Continue with other files
   - Report summary at end

4. **Search Failures**:
   - Return empty results
   - Log error details
   - Graceful degradation

## Performance Characteristics

### Indexing
- **Time**: ~1-2 seconds per file (embedding generation)
- **Memory**: Batched processing (100 files default)
- **Storage**: ~10KB per file (2560 floats × 4 bytes)

### Search
- **Time**: <100ms for typical collections
- **Scalability**: Up to 100K+ vectors with good performance

### Optimization Tips
1. Reduce `batch_size` for large files
2. Use smaller embedding model for faster indexing
3. Adjust `search_score_threshold` for precision/recall tradeoff

## Security Considerations

1. **Local Services**: Qdrant and Ollama run locally (localhost)
2. **No External Calls**: All data stays on local machine
3. **Docker Permissions**: Requires Docker access
4. **File Access**: Reads source files with project permissions

## Extension Points

The architecture supports future enhancements:

1. **Custom Embedding Models**: Swap Ollama for other providers
2. **Hybrid Search**: Combine vector + keyword search
3. **Incremental Indexing**: Index only changed files
4. **Multi-Model**: Different models for different file types
5. **Metadata Enrichment**: Add git blame, author info, etc.

## Dependencies

```
External Services:
- Docker (for Qdrant container)
- Qdrant (vector database)
- Ollama (embedding generation)

Python Packages:
- qdrant-client (official Python client)
- requests (HTTP requests, already in deps)
```

## Testing Strategy

1. **Unit Tests**: Individual components (Config, Client methods)
2. **Integration Tests**: Full workflow without services
3. **Manual Tests**: With actual Qdrant/Ollama
4. **Verification**: Syntax and structure checks

---

For usage examples, see `QDRANT_QUICKSTART.md`.
For implementation details, see `QDRANT_IMPLEMENTATION_SUMMARY.md`.
