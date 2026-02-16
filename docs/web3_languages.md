# Web3 Language Support

This document describes the native language server support for Web3 programming languages in Serena.

## Supported Web3 Languages

### 1. Solidity
- **File Extensions**: `.sol`
- **Language Server**: [@nomicfoundation/solidity-language-server](https://www.npmjs.com/package/@nomicfoundation/solidity-language-server)
- **Requirements**: 
  - Node.js and npm installed
  - Install with: `npm install -g @nomicfoundation/solidity-language-server`
  - Or use npx (automatic): npx will download and run the server automatically
- **Use Case**: Smart contracts for Ethereum and EVM-compatible blockchains
- **Test Repository**: `test/resources/repos/solidity/test_repo/`

### 2. Vyper
- **File Extensions**: `.vy`
- **Language Server**: vyper-lsp
- **Requirements**:
  - Python 3.x
  - Vyper compiler: `pip install vyper`
  - Language server: `pip install vyper-lsp`
- **Use Case**: Alternative smart contract language for Ethereum with Python-like syntax
- **Test Repository**: `test/resources/repos/vyper/test_repo/`

### 3. Move (Aptos/Diem)
- **File Extensions**: `.move`
- **Language Server**: move-analyzer
- **Requirements**:
  - Aptos CLI or Move toolchain
  - Install Aptos CLI: https://aptos.dev/tools/install-cli/
  - Install move-analyzer: `cargo install --git https://github.com/move-language/move move-analyzer`
- **Use Case**: Smart contracts for Aptos, Diem, and other Move-based blockchains
- **Test Repository**: `test/resources/repos/move/test_repo/`

### 4. Sui Move
- **File Extensions**: `.move`
- **Language Server**: sui-move-analyzer
- **Requirements**:
  - Sui CLI installed
  - Install Sui: https://docs.sui.io/guides/developer/getting-started/sui-install
  - sui-move-analyzer is typically included with Sui CLI
- **Use Case**: Smart contracts for Sui blockchain
- **Test Repository**: `test/resources/repos/sui_move/test_repo/`
- **Note**: Sui Move has some differences from standard Move

### 5. Cairo
- **File Extensions**: `.cairo`
- **Language Server**: cairo-language-server
- **Requirements**:
  - Scarb (Cairo package manager and toolchain)
  - Install Scarb: `curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh`
  - cairo-language-server is included with Scarb
- **Use Case**: Smart contracts for Starknet (Layer 2 on Ethereum)
- **Test Repository**: `test/resources/repos/cairo/test_repo/`

## Already Supported Languages

### Rust
- **File Extensions**: `.rs`
- **Language Server**: rust-analyzer
- **Use Case**: Substrate/Polkadot smart contracts, Solana programs
- Already implemented in the codebase

### Go
- **File Extensions**: `.go`
- **Language Server**: gopls
- **Use Case**: Cosmos SDK, Tendermint, various blockchain infrastructure
- Already implemented in the codebase

## Usage

### Using with Serena MCP Server

```bash
# Start the MCP server for a Web3 project
serena-mcp-server --project /path/to/web3/project

# The language will be automatically detected based on file extensions
```

### Programmatic Usage

```python
from serena.agent import SerenaAgent
from solidlsp.ls_config import Language, LanguageServerConfig

# Create agent for a Solidity project
agent = SerenaAgent(project="/path/to/solidity/project")

# Or explicitly specify the language
config = LanguageServerConfig(code_language=Language.SOLIDITY)
agent = SerenaAgent(project="/path/to/project", language_config=config)
```

### Testing

Run tests for specific Web3 languages:

```bash
# Test Solidity support
pytest test -m solidity

# Test Vyper support
pytest test -m vyper

# Test Move support
pytest test -m move

# Test Sui Move support
pytest test -m sui_move

# Test Cairo support
pytest test -m cairo

# Test all Web3 languages
pytest test -m "solidity or vyper or move or sui_move or cairo"
```

## Language Server Features

All Web3 language servers provide the following core LSP features:

- **Go to Definition**: Navigate to symbol definitions
- **Find References**: Find all references to a symbol
- **Document Symbols**: List all symbols in a file
- **Hover Information**: Show documentation and type information
- **Completion**: Auto-completion for identifiers
- **Diagnostics**: Real-time error and warning reporting

Specific features may vary by language server implementation.

## Project Structure Examples

### Solidity Project
```
my-solidity-project/
├── contracts/
│   ├── Token.sol
│   └── interfaces/
│       └── IERC20.sol
├── hardhat.config.js  # or foundry.toml
└── package.json
```

### Vyper Project
```
my-vyper-project/
├── contracts/
│   ├── token.vy
│   └── vault.vy
└── vyper_config.yaml
```

### Move Project
```
my-move-project/
├── Move.toml
└── sources/
    ├── coin.move
    └── nft.move
```

### Sui Move Project
```
my-sui-project/
├── Move.toml
└── sources/
    ├── collection.move
    └── marketplace.move
```

### Cairo Project
```
my-cairo-project/
├── Scarb.toml
└── src/
    ├── lib.cairo
    └── token.cairo
```

## Troubleshooting

### Language Server Not Found

If you get an error that a language server is not found:

1. Make sure the required toolchain is installed (see Requirements above)
2. Verify the language server binary is in your PATH
3. Check the specific installation instructions for each language

### Language Not Auto-Detected

If the language is not automatically detected:

1. Verify your files have the correct extension
2. Make sure you're in a project directory with appropriate config files (e.g., Move.toml, Scarb.toml)
3. Try explicitly specifying the language in your configuration

### Performance Issues

Some language servers (especially for large projects) may take time to initialize:

- **Solidity**: May need to download/compile dependencies via npm
- **Move/Sui Move**: Requires building the Move bytecode
- **Cairo**: Scarb needs to resolve and build dependencies

Be patient on first initialization, as language servers often cache results for subsequent runs.

## Contributing

To add support for additional Web3 languages:

1. Create a new language server class in `src/solidlsp/language_servers/`
2. Add the language to the `Language` enum in `src/solidlsp/ls_config.py`
3. Add file extension patterns in `get_source_fn_matcher()`
4. Map the language to its class in `get_ls_class()`
5. Create test repository in `test/resources/repos/`
6. Add pytest marker in `pyproject.toml`
7. Write tests for the new language

See existing implementations for examples.

## References

- [Solidity Language Server](https://www.npmjs.com/package/@nomicfoundation/solidity-language-server)
- [Vyper Documentation](https://docs.vyperlang.org/)
- [Move Language](https://github.com/move-language/move)
- [Aptos Documentation](https://aptos.dev/)
- [Sui Documentation](https://docs.sui.io/)
- [Cairo Documentation](https://www.cairo-lang.org/)
- [Scarb (Cairo Toolchain)](https://docs.swmansion.com/scarb/)
