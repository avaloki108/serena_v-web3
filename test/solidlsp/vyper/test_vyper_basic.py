import os

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import Language
from solidlsp.ls_utils import SymbolUtils


@pytest.mark.vyper
class TestVyperLanguageServer:
    @pytest.mark.parametrize("language_server", [Language.VYPER], indirect=True)
    def test_find_symbol(self, language_server: SolidLanguageServer) -> None:
        symbols = language_server.request_full_symbol_tree()
        assert SymbolUtils.symbol_tree_contains_name(symbols, "DemoContract"), "DemoContract not found in symbol tree"
        assert SymbolUtils.symbol_tree_contains_name(symbols, "increment"), "increment function not found in symbol tree"
        assert SymbolUtils.symbol_tree_contains_name(symbols, "HelperContract"), "HelperContract not found in symbol tree"

    @pytest.mark.parametrize("language_server", [Language.VYPER], indirect=True)
    def test_find_referencing_symbols(self, language_server: SolidLanguageServer) -> None:
        file_path = os.path.join("DemoContract.vy")
        symbols = language_server.request_document_symbols(file_path).get_all_symbols_and_roots()
        helper_symbol = None
        for sym in symbols[0]:
            if sym.get("name") == "helperCheckBalance":
                helper_symbol = sym
                break
        assert helper_symbol is not None, "Could not find 'helperCheckBalance' function symbol in DemoContract.vy"
        sel_start = helper_symbol["selectionRange"]["start"]
        refs = language_server.request_references(file_path, sel_start["line"], sel_start["character"])
        assert any("DemoContract.vy" in ref.get("uri", "") for ref in refs), "Expected at least one reference result to point at DemoContract.vy"
