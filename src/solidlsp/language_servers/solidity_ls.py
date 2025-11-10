"""
Provides Solidity specific instantiation of the LanguageServer class using solidity-language-server.
"""

import logging
import os
import shutil
import subprocess
import threading

from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.ls_logger import LanguageServerLogger
from solidlsp.ls_utils import PathUtils
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings


class SolidityLanguageServer(SolidLanguageServer):
    """
    Provides Solidity specific instantiation of the LanguageServer class using Nomicfoundation's solidity-language-server.
    """

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # Ignore common Solidity build/dependency directories
        return super().is_ignored_dirname(dirname) or dirname in [
            "node_modules",
            "artifacts",
            "cache",
            "out",
            "build",
            "dist",
        ]

    @staticmethod
    def _check_node_available():
        """Check if Node.js is available."""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            return None
        return None

    @staticmethod
    def _check_npm_available():
        """Check if npm is available."""
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            return None
        return None

    @staticmethod
    def _get_solidity_ls_path():
        """Get solidity-language-server path from npx or global installation."""
        # Try npx first (recommended)
        npx_path = shutil.which("npx")
        if npx_path:
            return ["npx", "--yes", "@nomicfoundation/solidity-language-server", "--stdio"]

        # Fallback to global installation
        ls_path = shutil.which("nomicfoundation-solidity-language-server")
        if ls_path:
            return [ls_path, "--stdio"]

        return None

    @staticmethod
    def _setup_runtime_dependency(logger: LanguageServerLogger):
        """
        Check if required Solidity language server dependencies are available.
        Raises RuntimeError with helpful message if dependencies are missing.
        """
        node_version = SolidityLanguageServer._check_node_available()
        if not node_version:
            raise RuntimeError(
                "Node.js is not installed. Please install Node.js from https://nodejs.org/ "
                "and make sure it is added to your PATH. The Solidity language server requires Node.js to run."
            )

        npm_version = SolidityLanguageServer._check_npm_available()
        if not npm_version:
            raise RuntimeError(
                "npm is not installed. Please install npm (usually comes with Node.js) from https://nodejs.org/ "
                "and make sure it is added to your PATH."
            )

        logger.log(f"Node.js version: {node_version}", logging.INFO)
        logger.log(f"npm version: {npm_version}", logging.INFO)

        ls_cmd = SolidityLanguageServer._get_solidity_ls_path()
        if not ls_cmd:
            raise RuntimeError(
                "Solidity language server not found.\n"
                "Please install it globally with:\n"
                "  npm install -g @nomicfoundation/solidity-language-server\n\n"
                "Or ensure 'npx' is available (comes with npm 5.2+) to use the server automatically."
            )

        logger.log(f"Using Solidity language server: {' '.join(ls_cmd)}", logging.INFO)
        return ls_cmd

    def __init__(
        self,
        config: LanguageServerConfig,
        logger: LanguageServerLogger,
        repository_root_path: str,
        solidlsp_settings: SolidLSPSettings,
    ):
        """
        Creates a SolidityLanguageServer instance. This class is not meant to be instantiated directly.
        Use LanguageServer.create() instead.
        """
        ls_cmd = self._setup_runtime_dependency(logger)

        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=ls_cmd, cwd=repository_root_path),
            "solidity",
            solidlsp_settings,
        )
        self.server_ready = threading.Event()

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the Solidity Language Server.
        """
        root_uri = PathUtils.path_to_uri(repository_absolute_path)
        return {
            "processId": os.getpid(),
            "locale": "en",
            "rootPath": repository_absolute_path,
            "rootUri": root_uri,
            "capabilities": {
                "textDocument": {
                    "synchronization": {"didSave": True, "dynamicRegistration": True},
                    "completion": {"dynamicRegistration": True, "completionItem": {"snippetSupport": True}},
                    "definition": {"dynamicRegistration": True, "linkSupport": True},
                    "references": {"dynamicRegistration": True},
                    "documentSymbol": {
                        "dynamicRegistration": True,
                        "hierarchicalDocumentSymbolSupport": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                    "hover": {"dynamicRegistration": True, "contentFormat": ["markdown", "plaintext"]},
                },
                "workspace": {
                    "workspaceFolders": True,
                    "didChangeConfiguration": {"dynamicRegistration": True},
                    "symbol": {"dynamicRegistration": True},
                },
            },
            "workspaceFolders": [
                {
                    "name": os.path.basename(repository_absolute_path),
                    "uri": root_uri,
                }
            ],
        }

    def _start_server(self):
        """Start solidity-language-server process"""

        def register_capability_handler(params):
            return

        def window_log_message(msg):
            self.logger.log(f"LSP: window/logMessage: {msg}", logging.INFO)

        def do_nothing(params):
            return

        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        self.logger.log("Starting Solidity language server process", logging.INFO)
        self.server.start()
        initialize_params = self._get_initialize_params(self.repository_root_path)

        self.logger.log(
            "Sending initialize request from LSP client to LSP server and awaiting response",
            logging.INFO,
        )
        init_response = self.server.send.initialize(initialize_params)

        # Verify server capabilities
        assert "textDocumentSync" in init_response["capabilities"]

        self.server.notify.initialized({})
        self.completions_available.set()

        # Solidity language server is typically ready immediately after initialization
        self.server_ready.set()
        self.server_ready.wait()
