"""
Provides Cairo specific instantiation of the LanguageServer class using cairo-language-server.
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


class CairoLanguageServer(SolidLanguageServer):
    """
    Provides Cairo specific instantiation of the LanguageServer class using cairo-language-server.
    Supports Cairo 1.0+ (Starknet).
    """

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # Ignore common Cairo build/dependency directories
        return super().is_ignored_dirname(dirname) or dirname in [
            "target",
            "build",
            ".scarb",
        ]

    @staticmethod
    def _check_cairo_available():
        """Check if Cairo/Scarb is available."""
        # Try scarb first (recommended Cairo toolchain manager)
        try:
            result = subprocess.run(["scarb", "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return ("scarb", result.stdout.strip())
        except FileNotFoundError:
            pass

        # Try cairo CLI
        try:
            result = subprocess.run(["cairo-compile", "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return ("cairo", result.stdout.strip())
        except FileNotFoundError:
            pass

        return None

    @staticmethod
    def _get_cairo_ls_path():
        """Get cairo-language-server path."""
        # Try to find cairo-language-server in PATH
        ls_path = shutil.which("cairo-language-server")
        if ls_path:
            return ls_path

        # Try scarb cairo-language-server
        scarb_path = shutil.which("scarb")
        if scarb_path:
            try:
                result = subprocess.run(
                    ["scarb", "cairo-language-server", "--version"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    return ["scarb", "cairo-language-server"]
            except (subprocess.SubprocessError, FileNotFoundError, OSError):
                pass

        # Alternative: look in ~/.cairo/bin
        home = os.path.expanduser("~")
        cairo_ls = os.path.join(home, ".cairo", "bin", "cairo-language-server")
        if os.path.exists(cairo_ls):
            return cairo_ls

        return None

    @staticmethod
    def _setup_runtime_dependency(logger: LanguageServerLogger):
        """
        Check if required Cairo language server dependencies are available.
        Raises RuntimeError with helpful message if dependencies are missing.
        """
        cairo_info = CairoLanguageServer._check_cairo_available()
        if not cairo_info:
            raise RuntimeError(
                "Cairo toolchain is not installed. Please install Scarb (recommended):\n\n"
                "Using Scarb (Cairo package manager and toolchain):\n"
                "  curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh\n\n"
                "Or install Cairo directly:\n"
                "  See https://www.cairo-lang.org/docs/quickstart.html\n\n"
                "Make sure the binaries are in your PATH."
            )

        tool_type, version = cairo_info
        logger.log(f"{tool_type} version: {version}", logging.INFO)

        ls_path = CairoLanguageServer._get_cairo_ls_path()
        if not ls_path:
            raise RuntimeError(
                "cairo-language-server not found.\n\n"
                "The Cairo language server should be included with Scarb.\n"
                "Please ensure you have Scarb installed:\n"
                "  curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh\n\n"
                "Or install the language server separately:\n"
                "  cargo install cairo-language-server\n\n"
                "Make sure the binary is in your PATH."
            )

        if isinstance(ls_path, list):
            logger.log(f"Using Cairo language server: {' '.join(ls_path)}", logging.INFO)
        else:
            logger.log(f"Using cairo-language-server at: {ls_path}", logging.INFO)

        return ls_path if isinstance(ls_path, list) else [ls_path]

    def __init__(
        self,
        config: LanguageServerConfig,
        logger: LanguageServerLogger,
        repository_root_path: str,
        solidlsp_settings: SolidLSPSettings,
    ):
        """
        Creates a CairoLanguageServer instance. This class is not meant to be instantiated directly.
        Use LanguageServer.create() instead.
        """
        ls_cmd = self._setup_runtime_dependency(logger)

        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=ls_cmd, cwd=repository_root_path),
            "cairo",
            solidlsp_settings,
        )
        self.server_ready = threading.Event()

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the Cairo Language Server.
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
        """Start cairo-language-server process"""

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

        self.logger.log("Starting Cairo language server process", logging.INFO)
        self.server.start()
        initialize_params = self._get_initialize_params(self.repository_root_path)

        self.logger.log(
            "Sending initialize request from LSP client to LSP server and awaiting response",
            logging.INFO,
        )
        init_response = self.server.send.initialize(initialize_params)

        # Verify server capabilities
        if "textDocumentSync" in init_response.get("capabilities", {}):
            self.logger.log("Cairo language server initialized successfully", logging.INFO)

        self.server.notify.initialized({})
        self.completions_available.set()

        # Server is ready after initialization
        self.server_ready.set()
        self.server_ready.wait()
