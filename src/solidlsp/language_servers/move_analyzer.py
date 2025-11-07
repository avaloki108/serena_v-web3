"""
Provides Move specific instantiation of the LanguageServer class using move-analyzer.
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


class MoveAnalyzer(SolidLanguageServer):
    """
    Provides Move specific instantiation of the LanguageServer class using move-analyzer.
    Supports Aptos Move and Diem Move.
    """

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # Ignore common Move build/dependency directories
        return super().is_ignored_dirname(dirname) or dirname in [
            "build",
            "target",
            ".aptos",
        ]

    @staticmethod
    def _check_move_available():
        """Check if Move CLI is available."""
        # Try aptos CLI first
        try:
            result = subprocess.run(["aptos", "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return ("aptos", result.stdout.strip())
        except FileNotFoundError:
            pass

        # Try move CLI
        try:
            result = subprocess.run(["move", "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return ("move", result.stdout.strip())
        except FileNotFoundError:
            pass

        return None

    @staticmethod
    def _get_move_analyzer_path():
        """Get move-analyzer path."""
        # Try to find move-analyzer in PATH
        analyzer_path = shutil.which("move-analyzer")
        if analyzer_path:
            return analyzer_path

        # Alternative paths where move-analyzer might be installed
        # For Aptos CLI, it might be in ~/.aptos/bin
        home = os.path.expanduser("~")
        aptos_analyzer = os.path.join(home, ".aptos", "bin", "move-analyzer")
        if os.path.exists(aptos_analyzer):
            return aptos_analyzer

        return None

    @staticmethod
    def _setup_runtime_dependency(logger: LanguageServerLogger):
        """
        Check if required Move analyzer dependencies are available.
        Raises RuntimeError with helpful message if dependencies are missing.
        """
        move_info = MoveAnalyzer._check_move_available()
        if not move_info:
            raise RuntimeError(
                "Move CLI or Aptos CLI is not installed. Please install one of:\n\n"
                "For Aptos Move:\n"
                "  See https://aptos.dev/tools/install-cli/ for installation instructions\n\n"
                "For Diem/Move:\n"
                "  See https://github.com/move-language/move for installation instructions"
            )

        cli_type, version = move_info
        logger.log(f"{cli_type} version: {version}", logging.INFO)

        analyzer_path = MoveAnalyzer._get_move_analyzer_path()
        if not analyzer_path:
            raise RuntimeError(
                "move-analyzer not found.\n\n"
                "For Aptos Move, install with:\n"
                "  cargo install --git https://github.com/move-language/move move-analyzer\n\n"
                "Make sure the binary is in your PATH or in ~/.aptos/bin/"
            )

        logger.log(f"Using move-analyzer at: {analyzer_path}", logging.INFO)
        return analyzer_path

    def __init__(
        self,
        config: LanguageServerConfig,
        logger: LanguageServerLogger,
        repository_root_path: str,
        solidlsp_settings: SolidLSPSettings,
    ):
        """
        Creates a MoveAnalyzer instance. This class is not meant to be instantiated directly.
        Use LanguageServer.create() instead.
        """
        analyzer_path = self._setup_runtime_dependency(logger)

        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=analyzer_path, cwd=repository_root_path),
            "move",
            solidlsp_settings,
        )
        self.server_ready = threading.Event()

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the Move Analyzer.
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
        """Start move-analyzer server process"""

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

        self.logger.log("Starting Move analyzer process", logging.INFO)
        self.server.start()
        initialize_params = self._get_initialize_params(self.repository_root_path)

        self.logger.log(
            "Sending initialize request from LSP client to LSP server and awaiting response",
            logging.INFO,
        )
        init_response = self.server.send.initialize(initialize_params)

        # Verify server capabilities
        if "textDocumentSync" in init_response.get("capabilities", {}):
            self.logger.log("Move analyzer initialized successfully", logging.INFO)

        self.server.notify.initialized({})
        self.completions_available.set()

        # Server is ready after initialization
        self.server_ready.set()
        self.server_ready.wait()
