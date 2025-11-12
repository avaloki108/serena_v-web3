"""
Web3 configuration settings for blockchain analysis and security scanning.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QdrantConfig:
    """Configuration for Qdrant vector database integration."""

    # Qdrant connection settings
    qdrant_url: str = "http://localhost:6333"
    collection_name_prefix: str = "serena_project"

    # Ollama embedding provider settings
    ollama_provider_url: str = "http://localhost:11434"
    embedding_model: str = "qwen3-embedding:4b"
    model_dimension: int = 2560

    # Search settings
    search_score_threshold: float = 0.80
    max_search_results: int = 20

    # Docker settings
    docker_container_name: str = "qdrant"
    enable_auto_start: bool = True

    # Indexing settings
    batch_size: int = 100
    enable_auto_indexing: bool = True

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "QdrantConfig":
        """Create QdrantConfig from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})

    def to_dict(self) -> dict[str, Any]:
        """Convert QdrantConfig to dictionary."""
        return {
            "qdrant_url": self.qdrant_url,
            "collection_name_prefix": self.collection_name_prefix,
            "ollama_provider_url": self.ollama_provider_url,
            "embedding_model": self.embedding_model,
            "model_dimension": self.model_dimension,
            "search_score_threshold": self.search_score_threshold,
            "max_search_results": self.max_search_results,
            "docker_container_name": self.docker_container_name,
            "enable_auto_start": self.enable_auto_start,
            "batch_size": self.batch_size,
            "enable_auto_indexing": self.enable_auto_indexing,
        }


@dataclass
class Web3Config:
    """Configuration for Web3 vulnerability hunting tools."""

    # Blockchain RPC endpoints
    ethereum_rpc_url: str = "https://eth.llamarpc.com"
    polygon_rpc_url: str = "https://polygon-rpc.com"
    bsc_rpc_url: str = "https://bsc-dataseed.binance.org"
    arbitrum_rpc_url: str = "https://arb1.arbitrum.io/rpc"
    optimism_rpc_url: str = "https://mainnet.optimism.io"

    # API keys for threat intelligence services
    etherscan_api_key: str = ""
    blocksec_api_key: str = ""
    chainanalysis_api_key: str = ""

    # Analysis settings
    default_severity_threshold: str = "medium"
    max_transaction_lookback: int = 1000
    enable_threat_intelligence: bool = True

    # Security scan settings
    smart_contract_analysis: dict[str, Any] = field(
        default_factory=lambda: {
            "check_reentrancy": True,
            "check_overflow": True,
            "check_access_control": True,
            "check_delegatecall": True,
            "check_tx_origin": True,
            "check_timestamp": True,
            "check_unchecked_calls": True,
        }
    )

    # DeFi protocol specific settings
    defi_protocol_checks: dict[str, Any] = field(
        default_factory=lambda: {
            "oracle_manipulation": True,
            "flash_loan_attack": True,
            "mev_protection": True,
            "liquidity_risk": True,
        }
    )

    # Transaction analysis settings
    transaction_analysis: dict[str, Any] = field(
        default_factory=lambda: {
            "check_mev": True,
            "check_flash_loan": True,
            "check_unusual_gas": True,
            "check_suspicious_calls": True,
            "check_token_approval": True,
            "high_gas_threshold": 1000000,
            "suspicious_gas_price_multiplier": 5.0,
        }
    )

    # Threat intelligence sources
    threat_intel_sources: list[str] = field(
        default_factory=lambda: [
            "etherscan",
            "chainabuse",
            "cryptoscamdb",
            "blocksec",
        ]
    )

    # Cache settings for performance
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "Web3Config":
        """Create Web3Config from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})

    def to_dict(self) -> dict[str, Any]:
        """Convert Web3Config to dictionary."""
        return {
            "ethereum_rpc_url": self.ethereum_rpc_url,
            "polygon_rpc_url": self.polygon_rpc_url,
            "bsc_rpc_url": self.bsc_rpc_url,
            "arbitrum_rpc_url": self.arbitrum_rpc_url,
            "optimism_rpc_url": self.optimism_rpc_url,
            "etherscan_api_key": self.etherscan_api_key,
            "blocksec_api_key": self.blocksec_api_key,
            "chainanalysis_api_key": self.chainanalysis_api_key,
            "default_severity_threshold": self.default_severity_threshold,
            "max_transaction_lookback": self.max_transaction_lookback,
            "enable_threat_intelligence": self.enable_threat_intelligence,
            "smart_contract_analysis": self.smart_contract_analysis,
            "defi_protocol_checks": self.defi_protocol_checks,
            "transaction_analysis": self.transaction_analysis,
            "threat_intel_sources": self.threat_intel_sources,
            "enable_cache": self.enable_cache,
            "cache_ttl_seconds": self.cache_ttl_seconds,
        }
