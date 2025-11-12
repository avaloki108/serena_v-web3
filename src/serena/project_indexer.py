"""
Qdrant indexing integration for Serena projects.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from serena.config.web3_config import QdrantConfig
from serena.qdrant_client import QdrantClient

if TYPE_CHECKING:
    from serena.project import Project

log = logging.getLogger(__name__)


class ProjectIndexer:
    """Handles automatic Qdrant indexing for projects."""

    def __init__(self, project: "Project"):
        """
        Initialize the project indexer.

        :param project: the project to index
        """
        self.project = project
        self.qdrant_config = project.project_config.qdrant_config or QdrantConfig()
        self.qdrant_client = QdrantClient(self.qdrant_config)
        self.collection_name = self.qdrant_client.get_collection_name(project.project_name)

    def index_project_files(self) -> None:
        """
        Index all project source files into Qdrant.
        """
        if not self.qdrant_config.enable_auto_indexing:
            log.info("Auto-indexing is disabled in configuration")
            return

        log.info(f"Starting Qdrant indexing for project '{self.project.project_name}'")

        # Gather all source files
        source_files = self.project.gather_source_files()
        log.info(f"Found {len(source_files)} source files to index")

        # Prepare documents for indexing
        documents = []
        for i, file_path in enumerate(source_files):
            try:
                # Read file content
                relative_path = Path(file_path).relative_to(self.project.project_root)
                content = self.project.read_file(str(relative_path))

                # Create document
                doc = {
                    "id": i,
                    "text": content,
                    "metadata": {
                        "file_path": str(relative_path),
                        "absolute_path": file_path,
                        "project_name": self.project.project_name,
                    },
                }
                documents.append(doc)

            except Exception as e:
                log.warning(f"Failed to read file {file_path}: {e}")
                continue

        if not documents:
            log.warning("No documents to index")
            return

        # Index documents
        try:
            self.qdrant_client.index_documents(self.collection_name, documents)
            log.info(f"Successfully indexed {len(documents)} documents to collection '{self.collection_name}'")
        except Exception as e:
            log.error(f"Failed to index documents: {e}")
            raise

    def search_in_project(self, query: str, limit: int | None = None) -> list[dict]:
        """
        Search for code in the project using semantic search.

        :param query: the search query
        :param limit: maximum number of results to return
        :return: list of search results
        """
        try:
            results = self.qdrant_client.search(self.collection_name, query, limit=limit)
            return results
        except Exception as e:
            log.error(f"Failed to search: {e}")
            return []

    def delete_project_index(self) -> None:
        """
        Delete the project's Qdrant index.
        """
        try:
            self.qdrant_client.delete_collection(self.collection_name)
            log.info(f"Deleted index for project '{self.project.project_name}'")
        except Exception as e:
            log.warning(f"Failed to delete project index: {e}")
