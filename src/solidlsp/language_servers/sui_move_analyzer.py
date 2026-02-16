"""
Provides Sui Move specific instantiation of the LanguageServer class using sui-move-analyzer.
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


class SuiMoveAnalyzer(SolidLanguageServer):
    """
    Provides Sui Move specific instantiation of the LanguageServer class using sui-move-analyzer.
    """

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # Ignore common Sui Move build/dependency directories
        return super().is_ignored_dirname(dirname) or dirname in [
            "build",
            "target",
            ".sui",
        ]

    @staticmethod
    def _check_sui_available():
        """Check if Sui CLI is available."""
        try:
            result = subprocess.run(["sui", "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            return None
        return None

    @staticmethod
    def _get_sui_move_analyzer_path():
        """Get sui-move-analyzer path."""
        # Try to find sui-move-analyzer in PATH
        analyzer_path = shutil.which("sui-move-analyzer")
        if analyzer_path:
            return analyzer_path

        # Try as sui subcommand
        sui_path = shutil.which("sui")
        if sui_path:
            # Check if 'sui move-analyzer' command exists
            try:
                result = subprocess.run(
                    ["sui", "move-analyzer", "--help"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    return ["sui", "move-analyzer"]
            except (subprocess.SubprocessError, FileNotFoundError, OSError):
                pass

        # Alternative: look in ~/.sui/bin
        home = os.path.expanduser("~")
        sui_analyzer = os.path.join(home, ".sui", "bin", "sui-move-analyzer")
        if os.path.exists(sui_analyzer):
            return sui_analyzer

        return None

    @staticmethod
    def _setup_runtime_dependency(logger: LanguageServerLogger):
        """
        Check if required Sui Move analyzer dependencies are available.
        Raises RuntimeError with helpful message if dependencies are missing.
        """
        sui_version = SuiMoveAnalyzer._check_sui_available()
        if not sui_version:
            raise RuntimeError(
                "Sui CLI is not installed. Please install Sui:\n\n"
                "Using Homebrew (macOS/Linux):\n"
                "  brew install sui\n\n"
                "Or download from:\n"
                "  https://docs.sui.io/guides/developer/getting-started/sui-install\n\n"
                "Make sure the Sui binary is in your PATH."
            )

        logger.log(f"Sui version: {sui_version}", logging.INFO)

        analyzer_path = SuiMoveAnalyzer._get_sui_move_analyzer_path()
        if not analyzer_path:
            raise RuntimeError(
                "sui-move-analyzer not found.\n\n"
                "The Sui Move analyzer should be included with the Sui CLI.\n"
                "Please ensure you have the latest version of Sui installed:\n"
                "  https://docs.sui.io/guides/developer/getting-started/sui-install\n\n"
                "Or install it separately:\n"
                "  cargo install --git https://github.com/MystenLabs/sui sui-move-analyzer"
            )

        if isinstance(analyzer_path, list):
            logger.log(f"Using Sui Move analyzer: {' '.join(analyzer_path)}", logging.INFO)
        else:
            logger.log(f"Using sui-move-analyzer at: {analyzer_path}", logging.INFO)

        return analyzer_path if isinstance(analyzer_path, list) else [analyzer_path]

    def __init__(
        self,
        config: LanguageServerConfig,
        repository_root_path: str,
        solidlsp_settings: SolidLSPSettings,
    ):
        """
        Creates a SuiMoveAnalyzer instance. This class is not meant to be instantiated directly.
        Use LanguageServer.create() instead.
        """
        logger = LanguageServerLogger("sui_move")
        analyzer_cmd = self._setup_runtime_dependency(logger)

        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=analyzer_cmd, cwd=repository_root_path),
            "sui_move",
            solidlsp_settings,
        )
        self.server_ready = threading.Event()

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the Sui Move Analyzer.
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
        """Start sui-move-analyzer server process"""

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

        self.logger.log("Starting Sui Move analyzer process", logging.INFO)
        self.server.start()
        initialize_params = self._get_initialize_params(self.repository_root_path)

        self.logger.log(
            "Sending initialize request from LSP client to LSP server and awaiting response",
            logging.INFO,
        )
        init_response = self.server.send.initialize(initialize_params)

        # Verify server capabilities
        if "textDocumentSync" in init_response.get("capabilities", {}):
            self.logger.log("Sui Move analyzer initialized successfully", logging.INFO)

        self.server.notify.initialized({})
        self.completions_available.set()

        # Server is ready after initialization
        self.server_ready.set()
        self.server_ready.wait()
