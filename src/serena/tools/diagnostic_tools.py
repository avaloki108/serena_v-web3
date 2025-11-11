"""
Diagnostic tools for checking language server status and Web3 language server availability.
"""

import json
import shutil
from typing import Any

from serena.tools import Tool, ToolMarkerOptional
from solidlsp.ls_config import Language


class CheckLanguageServerStatusTool(Tool, ToolMarkerOptional):
    """
    Checks the status of language servers and provides diagnostic information.
    """

    def apply(self) -> str:
        """
        Check which language servers are running, which failed to start, and provide
        installation commands for missing language servers.

        :return: JSON string with language server status information
        """
        result: dict[str, Any] = {
            "language_server_manager_initialized": False,
            "languages_configured": [],
            "servers_running": [],
            "servers_failed": [],
            "installation_instructions": {},
        }

        # Check if we have an active project
        project = self.agent.get_active_project()
        if project is None:
            result["error"] = "No active project. Activate a project first."
            return json.dumps(result, indent=2)

        # Get configured languages
        configured_languages = [lang.value for lang in project.project_config.languages]
        result["languages_configured"] = configured_languages

        # Check if language server manager is initialized
        ls_manager = self.agent.get_language_server_manager()
        if ls_manager is None:
            result["language_server_manager_initialized"] = False
            result["message"] = "Language server manager is not initialized. This may happen if:"
            result["possible_causes"] = [
                "Language server initialization is still in progress (asynchronous)",
                "Language server failed to start during project activation",
                "Language server binaries are not installed",
            ]
            result["recommendation"] = "Try using a symbol tool (like get_symbols_overview) which will attempt lazy initialization."
        else:
            result["language_server_manager_initialized"] = True
            
            # Check which servers are running
            for language in project.project_config.languages:
                try:
                    ls = ls_manager.get_language_server(relative_path="")
                    if ls is not None and ls.is_running():
                        result["servers_running"].append(language.value)
                    else:
                        result["servers_failed"].append(language.value)
                except Exception as e:
                    result["servers_failed"].append(f"{language.value} (error: {e})")

        # Add installation instructions for common Web3 language servers
        result["installation_instructions"] = self._get_web3_ls_installation_instructions()

        return json.dumps(result, indent=2)

    def _get_web3_ls_installation_instructions(self) -> dict[str, dict[str, Any]]:
        """
        Get installation instructions for Web3 language servers.
        
        :return: Dictionary with installation instructions for each language
        """
        instructions = {}

        # Check for rust-analyzer (Rust/Soroban)
        rust_analyzer_path = shutil.which("rust-analyzer")
        instructions["rust"] = {
            "language_server": "rust-analyzer",
            "installed": rust_analyzer_path is not None,
            "path": rust_analyzer_path or "Not found",
            "install_command": "rustup component add rust-analyzer",
            "alternative_install": "Or install via package manager: apt install rust-analyzer / brew install rust-analyzer",
            "required_for": ["Rust", "Soroban smart contracts"],
        }

        # Check for solidity-language-server (Solidity)
        solidity_ls_path = shutil.which("solidity-language-server")
        instructions["solidity"] = {
            "language_server": "solidity-language-server",
            "installed": solidity_ls_path is not None,
            "path": solidity_ls_path or "Not found",
            "install_command": "npm install -g @nomicfoundation/solidity-language-server",
            "required_for": ["Solidity smart contracts"],
        }

        # Check for cairo-language-server (Cairo/Starknet)
        cairo_ls_path = shutil.which("cairo-language-server")
        instructions["cairo"] = {
            "language_server": "cairo-language-server",
            "installed": cairo_ls_path is not None,
            "path": cairo_ls_path or "Not found",
            "install_command": "cargo install cairo-language-server",
            "required_for": ["Cairo", "Starknet smart contracts"],
        }

        # Check for move-analyzer (Move/Aptos/Sui)
        move_analyzer_path = shutil.which("move-analyzer")
        instructions["move"] = {
            "language_server": "move-analyzer",
            "installed": move_analyzer_path is not None,
            "path": move_analyzer_path or "Not found",
            "install_command": "cargo install --git https://github.com/move-language/move move-analyzer",
            "required_for": ["Move", "Aptos", "Sui smart contracts"],
        }

        # Check for vyper-lsp (Vyper)
        vyper_lsp_path = shutil.which("vyper-lsp")
        instructions["vyper"] = {
            "language_server": "vyper-lsp",
            "installed": vyper_lsp_path is not None,
            "path": vyper_lsp_path or "Not found",
            "install_command": "pip install vyper-lsp",
            "required_for": ["Vyper smart contracts"],
        }

        return instructions


class DetectWeb3LanguagesTool(Tool, ToolMarkerOptional):
    """
    Detects which Web3-related programming languages are present in the project.
    """

    def apply(self) -> str:
        """
        Detect which Web3 programming languages are used in the project based on file extensions
        and project structure.

        :return: JSON string with detected Web3 languages
        """
        project = self.agent.get_active_project()
        if project is None:
            return json.dumps({"error": "No active project. Activate a project first."})

        detected_languages = {
            "rust_soroban": False,
            "solidity": False,
            "vyper": False,
            "cairo": False,
            "move": False,
        }

        # Gather source files
        try:
            source_files = project.gather_source_files()

            # Detect Rust/Soroban
            if any(f.endswith(".rs") for f in source_files):
                detected_languages["rust_soroban"] = True

            # Detect Solidity
            if any(f.endswith(".sol") for f in source_files):
                detected_languages["solidity"] = True

            # Detect Vyper
            if any(f.endswith(".vy") for f in source_files):
                detected_languages["vyper"] = True

            # Detect Cairo
            if any(f.endswith(".cairo") for f in source_files):
                detected_languages["cairo"] = True

            # Detect Move
            if any(f.endswith(".move") for f in source_files):
                detected_languages["move"] = True

        except Exception as e:
            return json.dumps({"error": f"Failed to gather source files: {e}"})

        result = {
            "project": project.project_name,
            "detected_languages": [lang for lang, detected in detected_languages.items() if detected],
            "configured_languages": [lang.value for lang in project.project_config.languages],
            "recommendations": [],
        }

        # Add recommendations
        if detected_languages["rust_soroban"] and Language.RUST not in project.project_config.languages:
            result["recommendations"].append("Add Rust to project configuration for Soroban development")

        if detected_languages["solidity"]:
            result["recommendations"].append("Ensure solidity-language-server is installed for Solidity support")

        if detected_languages["vyper"]:
            result["recommendations"].append("Ensure vyper-lsp is installed for Vyper support")

        if detected_languages["cairo"]:
            result["recommendations"].append("Ensure cairo-language-server is installed for Cairo/Starknet support")

        if detected_languages["move"]:
            result["recommendations"].append("Ensure move-analyzer is installed for Move/Aptos/Sui support")

        return json.dumps(result, indent=2)
