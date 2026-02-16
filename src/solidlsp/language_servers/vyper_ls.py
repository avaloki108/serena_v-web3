"""
Provides Vyper specific instantiation of LanguageServer class.
"""

import logging
import os
import shutil
import subprocess
import threading

from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.ls_utils import PathUtils
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings

log = logging.getLogger(__name__)

class VyperLanguageServer(SolidLanguageServer):
    """
    Provides Vyper specific instantiation of LanguageServer class.
    Uses vyper-lsp if available.
    """

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # Ignore common Vyper build/dependency directories
        return super().is_ignored_dirname(dirname) or dirname in [
            "__pycache__",
            "build",
            "out",
            ".pytest_cache",
        ]

    @staticmethod
    def _check_vyper_available():
        """Check if Vyper compiler is available."""
        try:
            result = subprocess.run(["vyper", "--version"], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            return None
        return None

    @staticmethod
    def _get_vyper_lsp_path():
        """Get vyper-lsp path."""
        # Try to find vyper-lsp in PATH
        lsp_path = shutil.which("vyper-lsp")
        if lsp_path:
            return lsp_path

        # Alternative: python -m vyper_lsp
        python_path = shutil.which("python3") or shutil.which("python")
        if python_path:
            # Check if vyper_lsp module is available
            try:
                result = subprocess.run(
                    [python_path, "-c", "import vyper_lsp"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    return [python_path, "-m", "vyper_lsp"]
            except:
                pass

        return None

    @staticmethod
    def _setup_runtime_dependency():
        """
        Check if required Vyper language server dependencies are available.
        Raises RuntimeError with helpful message if dependencies are missing.
        """
        vyper_version = VyperLanguageServer._check_vyper_available()
        if not vyper_version:
            raise RuntimeError(
                "Vyper compiler is not installed. Please install Vyper:\n"
                "  pip install vyper\n"
                "See https://docs.vyperlang.org/en/stable/installing-vyper.html for more information."
            )

        log.info(f"Vyper version: {vyper_version}")

        ls_cmd = VyperLanguageServer._get_vyper_lsp_path()
        if not ls_cmd:
            raise RuntimeError(
                "Vyper language server not found.\n"
                "Please install vyper-lsp:\n"
                "  pip install vyper-lsp\n"
                "Note: Vyper LSP support may be limited or under development."
            )

        log.info(f"Using Vyper language server: {ls_cmd if isinstance(ls_cmd, str) else ' '.join(ls_cmd)}")
        return ls_cmd if isinstance(ls_cmd, list) else [ls_cmd]

    def __init__(
        self,
        config: LanguageServerConfig,
        repository_root_path: str,
        solidlsp_settings: SolidLSPSettings,
    ):
        """
        Creates a VyperLanguageServer instance. This class is not meant to be instantiated directly.
        Use LanguageServer.create() instead.
        """
        ls_cmd = self._setup_runtime_dependency()

        super().__init__(
            config,
            repository_root_path,
            ProcessLaunchInfo(cmd=ls_cmd, cwd=repository_root_path),
            "vyper",
            solidlsp_settings,
        )
        self.server_ready = threading.Event()

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for Vyper Language Server.
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
        """Start vyper-lsp server process"""

        def register_capability_handler(params):
            return

        def do_nothing(params):
            return

        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        log.info("Starting Vyper language server process")
        self.server.start()
        initialize_params = self._get_initialize_params(self.repository_root_path)

        log.info(
            "Sending initialize request from LSP client to LSP server and awaiting response",
        )

        init_response = self.server.send.initialize(initialize_params)

        # Verify server capabilities if available
        if "textDocumentSync" in init_response.get("capabilities", {}):
            log.info("Vyper language server initialized successfully")

        self.server.notify.initialized({})
        self.completions_available.set()

        # Server is ready after initialization
        self.server_ready.set()
        self.server_ready.wait()
