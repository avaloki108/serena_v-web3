"""
Qdrant vector database client for project indexing and semantic search.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

import requests

from serena.config.web3_config import QdrantConfig

log = logging.getLogger(__name__)


class QdrantClientError(Exception):
    """Exception raised for Qdrant client errors."""

    pass


class QdrantClient:
    """Client for interacting with Qdrant vector database."""

    def __init__(self, config: QdrantConfig):
        """
        Initialize the Qdrant client.

        :param config: QdrantConfig instance with connection and model settings
        """
        self.config = config
        self._ensure_qdrant_running()

    def _ensure_qdrant_running(self) -> None:
        """
        Ensure Qdrant is running, attempting to start it if configured to do so.
        """
        if not self.config.enable_auto_start:
            if not self.is_qdrant_running():
                raise QdrantClientError("Qdrant is not running and auto-start is disabled")
            return

        if not self.is_qdrant_running():
            log.info(f"Qdrant is not running, attempting to start container '{self.config.docker_container_name}'")
            try:
                self._start_qdrant_docker()
            except Exception as e:
                raise QdrantClientError(f"Failed to start Qdrant: {e}") from e

    def is_qdrant_running(self) -> bool:
        """
        Check if Qdrant is running and accessible.

        :return: True if Qdrant is running and responding to health checks
        """
        try:
            response = requests.get(f"{self.config.qdrant_url}/healthz", timeout=5)
            return response.status_code == 200
        except Exception as e:
            log.debug(f"Qdrant health check failed: {e}")
            return False

    def _start_qdrant_docker(self) -> None:
        """
        Start Qdrant using Docker.
        """
        try:
            # First check if container exists
            check_cmd = ["docker", "ps", "-a", "--filter", f"name={self.config.docker_container_name}", "--format", "{{.Names}}"]
            result = subprocess.run(check_cmd, capture_output=True, text=True, check=True, timeout=10)

            if self.config.docker_container_name in result.stdout:
                # Container exists, try to start it
                log.info(f"Starting existing Docker container '{self.config.docker_container_name}'")
                subprocess.run(["docker", "start", self.config.docker_container_name], check=True, timeout=30)
            else:
                # Container doesn't exist, create and run it
                log.info(f"Creating new Docker container '{self.config.docker_container_name}'")
                subprocess.run(
                    [
                        "docker",
                        "run",
                        "-d",
                        "--name",
                        self.config.docker_container_name,
                        "-p",
                        "6333:6333",
                        "-p",
                        "6334:6334",
                        "qdrant/qdrant",
                    ],
                    check=True,
                    timeout=60,
                )

            # Wait for Qdrant to become healthy
            import time

            max_wait = 30
            waited = 0
            while waited < max_wait:
                if self.is_qdrant_running():
                    log.info("Qdrant is now running and healthy")
                    return
                time.sleep(1)
                waited += 1

            raise QdrantClientError(f"Qdrant did not become healthy within {max_wait} seconds")

        except subprocess.CalledProcessError as e:
            raise QdrantClientError(f"Docker command failed: {e}") from e
        except subprocess.TimeoutExpired as e:
            raise QdrantClientError(f"Docker command timed out: {e}") from e

    def get_collection_name(self, project_name: str) -> str:
        """
        Get the collection name for a project.

        :param project_name: the project name
        :return: the collection name to use in Qdrant
        """
        # Sanitize project name for use in collection name
        safe_name = project_name.replace(" ", "_").replace("-", "_").lower()
        return f"{self.config.collection_name_prefix}_{safe_name}"

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in Qdrant.

        :param collection_name: the name of the collection
        :return: True if the collection exists
        """
        try:
            response = requests.get(f"{self.config.qdrant_url}/collections/{collection_name}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            log.debug(f"Error checking if collection exists: {e}")
            return False

    def create_collection(self, collection_name: str) -> None:
        """
        Create a new collection in Qdrant.

        :param collection_name: the name of the collection to create
        """
        if self.collection_exists(collection_name):
            log.info(f"Collection '{collection_name}' already exists")
            return

        payload = {
            "vectors": {
                "size": self.config.model_dimension,
                "distance": "Cosine",
            }
        }

        try:
            response = requests.put(f"{self.config.qdrant_url}/collections/{collection_name}", json=payload, timeout=30)
            response.raise_for_status()
            log.info(f"Created collection '{collection_name}'")
        except Exception as e:
            raise QdrantClientError(f"Failed to create collection: {e}") from e

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for the given text using Ollama.

        :param text: the text to embed
        :return: the embedding vector
        """
        try:
            payload = {"model": self.config.embedding_model, "prompt": text}

            response = requests.post(f"{self.config.ollama_provider_url}/api/embeddings", json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()
            return result["embedding"]
        except Exception as e:
            raise QdrantClientError(f"Failed to generate embedding: {e}") from e

    def index_documents(self, collection_name: str, documents: list[dict[str, Any]]) -> None:
        """
        Index a batch of documents into Qdrant.

        :param collection_name: the name of the collection
        :param documents: list of documents, each containing 'id', 'text', and optional 'metadata'
        """
        if not documents:
            return

        # Ensure collection exists
        if not self.collection_exists(collection_name):
            self.create_collection(collection_name)

        # Process documents in batches
        batch_size = self.config.batch_size
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            points = []

            for doc in batch:
                doc_id = doc["id"]
                text = doc["text"]
                metadata = doc.get("metadata", {})

                # Generate embedding
                embedding = self.generate_embedding(text)

                point = {"id": doc_id, "vector": embedding, "payload": {"text": text, **metadata}}
                points.append(point)

            # Upload points to Qdrant
            try:
                payload = {"points": points}
                response = requests.put(f"{self.config.qdrant_url}/collections/{collection_name}/points", json=payload, timeout=60)
                response.raise_for_status()
                log.info(f"Indexed {len(points)} documents to collection '{collection_name}'")
            except Exception as e:
                raise QdrantClientError(f"Failed to index documents: {e}") from e

    def search(self, collection_name: str, query_text: str, limit: Optional[int] = None) -> list[dict[str, Any]]:
        """
        Search for similar documents in a collection.

        :param collection_name: the name of the collection to search
        :param query_text: the query text
        :param limit: maximum number of results to return (defaults to config.max_search_results)
        :return: list of search results with score and payload
        """
        if not self.collection_exists(collection_name):
            log.warning(f"Collection '{collection_name}' does not exist")
            return []

        # Generate embedding for query
        query_embedding = self.generate_embedding(query_text)

        # Perform search
        limit = limit or self.config.max_search_results
        payload = {
            "vector": query_embedding,
            "limit": limit,
            "with_payload": True,
            "score_threshold": self.config.search_score_threshold,
        }

        try:
            response = requests.post(f"{self.config.qdrant_url}/collections/{collection_name}/points/search", json=payload, timeout=30)
            response.raise_for_status()

            results = response.json()
            return results.get("result", [])
        except Exception as e:
            raise QdrantClientError(f"Failed to search: {e}") from e

    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection from Qdrant.

        :param collection_name: the name of the collection to delete
        """
        try:
            response = requests.delete(f"{self.config.qdrant_url}/collections/{collection_name}", timeout=30)
            response.raise_for_status()
            log.info(f"Deleted collection '{collection_name}'")
        except Exception as e:
            log.warning(f"Failed to delete collection: {e}")
