# Web3 Vulnerability Hunting with Serena

Serena now includes comprehensive Web3 security analysis capabilities for smart contract auditing, blockchain transaction inspection, and DeFi protocol security assessment.

## Features

### 1. Smart Contract Analysis

Analyze smart contracts for common vulnerabilities:

- **Reentrancy attacks**
- **Integer overflow/underflow**
- **Unprotected functions**
- **tx.origin usage**
- **Unsafe delegatecall**
- **Timestamp dependence**
- **Unchecked external calls**
- **Access control issues**

#### Usage Example

```python
from serena.tools.web3_tools import AnalyzeSmartContractTool

tool = AnalyzeSmartContractTool(agent)
result = tool.apply(
    relative_path="contracts/MyToken.sol",
    vulnerability_types=["reentrancy", "overflow", "unprotected_functions"],
    severity_threshold="medium"
)
```

#### Supported Languages

- **Solidity** (.sol files) - Ethereum, BSC, Polygon, etc.
- **Vyper** (.vy files) - Alternative to Solidity
- **Rust** (.rs files) - Soroban smart contracts (Stellar)

#### Language Server Enhanced Analysis

Serena can leverage language servers for deeper vulnerability analysis when available. Language server-based analysis provides:

- **Symbol-level tracking**: Track vulnerable patterns through function call graphs
- **Cross-file analysis**: Find vulnerabilities that span multiple files
- **More accurate detection**: Reduce false positives with semantic understanding
- **Faster analysis**: Cached symbol information speeds up repeated checks

**Language Server Requirements:**

For enhanced analysis, install the appropriate language servers:

| Language | Language Server | Installation |
|----------|----------------|--------------|
| Rust/Soroban | rust-analyzer | `rustup component add rust-analyzer` |
| Solidity | solidity-language-server | `npm install -g @nomicfoundation/solidity-language-server` |
| Vyper | vyper-lsp | `pip install vyper-lsp` |

**Check Language Server Status:**

Use the diagnostic tool to check which language servers are available:

```python
from serena.tools.diagnostic_tools import CheckLanguageServerStatusTool

tool = CheckLanguageServerStatusTool(agent)
status = tool.apply()
print(status)  # Shows which servers are running and installation instructions
```

**Fallback Behavior:**

If language servers are not available, Serena automatically falls back to pattern-based analysis. This still provides valuable security insights, though with slightly less accuracy than language server-enhanced analysis.

To force pattern-based analysis even when language servers are available:

```python
result = tool.apply(
    relative_path="contracts/MyToken.sol",
    use_language_server=False  # Disable language server enhancement
)
```

### 2. Transaction Analysis

Analyze blockchain transactions for suspicious patterns:

- **MEV (Maximal Extractable Value)** detection
- **Flash loan attacks**
- **Unusual gas usage**
- **Suspicious contract calls** (selfdestruct, delegatecall)
- **Risky token approvals**

#### Usage Example

```python
from serena.tools.web3_tools import AnalyzeTransactionTool

tool = AnalyzeTransactionTool(agent)
result = tool.apply(
    transaction_data={
        "gas_limit": 300000,
        "gas_price": 50,
        "calls": [
            {"method": "swap", "target": "uniswap"},
            {"method": "transfer", "target": "0x123..."}
        ]
    },
    check_types=["mev", "flash_loan", "suspicious_calls"]
)
```

### 3. DeFi Protocol Security

Check DeFi protocols for security best practices:

#### Lending Protocols
- Oracle manipulation risks
- Liquidation mechanism checks
- Collateral factor validation

#### DEX Protocols
- Slippage protection
- MEV protection mechanisms
- Liquidity risk assessment

#### Staking Protocols
- Lock period configurations
- Reward rate sustainability
- Economic attack vectors

#### Usage Example

```python
from serena.tools.web3_tools import CheckDeFiProtocolTool

tool = CheckDeFiProtocolTool(agent)
result = tool.apply(
    protocol_config_path="config/lending_protocol.json",
    protocol_type="lending"
)
```

### 4. Threat Intelligence Integration

Check addresses and contracts against Web3 threat databases:

- **Scam detection**
- **Phishing databases**
- **Hack/exploit tracking**
- **Sanctions list checking** (OFAC, etc.)

#### Usage Example

```python
from serena.tools.web3_tools import Web3ThreatIntelligenceTool

tool = Web3ThreatIntelligenceTool(agent)
result = tool.apply(
    address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    check_type="all"  # or "scam", "phishing", "hack", "sanctions"
)
```

## Configuration

### Web3 Configuration File

Create a `.serena/web3_config.yml` file in your project:

```yaml
# Blockchain RPC endpoints
ethereum_rpc_url: "https://eth.llamarpc.com"
polygon_rpc_url: "https://polygon-rpc.com"
bsc_rpc_url: "https://bsc-dataseed.binance.org"
arbitrum_rpc_url: "https://arb1.arbitrum.io/rpc"
optimism_rpc_url: "https://mainnet.optimism.io"

# API keys for threat intelligence services
etherscan_api_key: "YOUR_API_KEY"
blocksec_api_key: "YOUR_API_KEY"
chainanalysis_api_key: "YOUR_API_KEY"

# Analysis settings
default_severity_threshold: "medium"
max_transaction_lookback: 1000
enable_threat_intelligence: true

# Smart contract analysis settings
smart_contract_analysis:
  check_reentrancy: true
  check_overflow: true
  check_access_control: true
  check_delegatecall: true
  check_tx_origin: true
  check_timestamp: true
  check_unchecked_calls: true

# DeFi protocol checks
defi_protocol_checks:
  oracle_manipulation: true
  flash_loan_attack: true
  mev_protection: true
  liquidity_risk: true

# Transaction analysis settings
transaction_analysis:
  check_mev: true
  check_flash_loan: true
  check_unusual_gas: true
  check_suspicious_calls: true
  check_token_approval: true
  high_gas_threshold: 1000000
  suspicious_gas_price_multiplier: 5.0

# Threat intelligence sources
threat_intel_sources:
  - etherscan
  - chainabuse
  - cryptoscamdb
  - blocksec

# Cache settings
enable_cache: true
cache_ttl_seconds: 3600
```

### Environment Variables

You can also set configuration via environment variables:

```bash
export ETHEREUM_RPC_URL="https://eth.llamarpc.com"
export ETHERSCAN_API_KEY="your_api_key"
export WEB3_SEVERITY_THRESHOLD="high"
```

## Integration with Serena Agent

The Web3 tools are automatically registered with the Serena agent and available through:

1. **MCP Server** - Use directly in Claude Code, Claude Desktop, or other MCP clients
2. **Python API** - Import and use in your custom agents
3. **CLI** - Access via Serena command-line interface

### Example: Using in Claude Code

```bash
# Start Serena MCP server
serena-mcp-server --project /path/to/web3/project

# In Claude Code, use tools like:
# "Analyze the smart contract at contracts/Token.sol for vulnerabilities"
# "Check if address 0x123... is associated with any known scams"
# "Analyze this transaction data for MEV attacks"
```

## Best Practices

### Smart Contract Analysis

1. **Run before deployment**: Always analyze contracts before deploying to mainnet
2. **Use appropriate severity threshold**: Start with "low" for comprehensive checks
3. **Combine with formal verification**: Use tools like Certora alongside Serena
4. **Review all findings**: Even low-severity issues can compound

### Transaction Analysis

1. **Pre-flight checks**: Analyze transactions before broadcasting
2. **Monitor for MEV**: Check high-value transactions for sandwich attack risk
3. **Validate gas prices**: Ensure gas settings are reasonable
4. **Check approvals**: Never approve unlimited token amounts without review

### DeFi Protocol Security

1. **Regular audits**: Check protocol configurations periodically
2. **Monitor oracle health**: Ensure price feed integrity
3. **Test liquidation mechanisms**: Verify liquidations work as expected
4. **Review upgrade paths**: Audit any proxy or upgrade mechanisms

### Threat Intelligence

1. **Check before interaction**: Validate addresses before sending funds
2. **Cross-reference sources**: Use multiple threat intel sources
3. **Report suspicious addresses**: Contribute to community databases
4. **Stay updated**: Refresh threat intelligence data regularly

## Advanced Features

### Custom Vulnerability Patterns

You can extend the analysis tools with custom patterns:

```python
from serena.tools.web3_tools import AnalyzeSmartContractTool

class CustomContractAnalyzer(AnalyzeSmartContractTool):
    def _check_custom_pattern(self, content: str):
        # Your custom vulnerability detection logic
        pass
```

### Integration with CI/CD

Add Web3 security checks to your CI/CD pipeline:

```yaml
# .github/workflows/security.yml
name: Web3 Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Serena Web3 Analysis
        run: |
          serena analyze-contracts --path contracts/ --threshold high
```

### Batch Analysis

Analyze multiple contracts or transactions:

```python
import glob
from serena.tools.web3_tools import AnalyzeSmartContractTool

tool = AnalyzeSmartContractTool(agent)

for contract_file in glob.glob("contracts/**/*.sol", recursive=True):
    result = tool.apply(contract_file)
    print(f"Analysis of {contract_file}: {result}")
```

## Troubleshooting

### Language Server Issues

#### Issue: "Language server manager is not initialized"

**Symptoms**: Symbol-based tools fail with message about language server not being initialized.

**Solutions**:

1. **Check Language Server Installation**:
   ```bash
   # For Rust/Soroban
   rustup component list | grep rust-analyzer
   which rust-analyzer
   
   # For Solidity
   npm list -g @nomicfoundation/solidity-language-server
   which solidity-language-server
   ```

2. **Use Diagnostic Tool**:
   ```python
   from serena.tools.diagnostic_tools import CheckLanguageServerStatusTool
   
   tool = CheckLanguageServerStatusTool(agent)
   print(tool.apply())
   ```

3. **Manual Initialization**:
   The language server is initialized asynchronously during project activation. If you try to use symbol tools immediately, use the lazy initialization by simply calling the tool - it will automatically attempt to initialize the language server.

4. **Check Logs**:
   Inspect Serena's logs for detailed error messages about why language servers failed to start. Common issues:
   - Language server binary not found in PATH
   - Permission issues
   - Incompatible versions
   - Missing dependencies

5. **Fallback to File-Based Tools**:
   If language servers cannot be initialized, use file-based tools:
   - `read_file` - Read contract source code
   - `search_for_pattern` - Search for patterns across files
   - `replace_regex` - Make changes using regex
   - Web3 tools with `use_language_server=False`

#### Issue: "Rust analyzer not found"

**Solution**: 
```bash
# Install via rustup (recommended)
rustup component add rust-analyzer

# Or via package manager
# Ubuntu/Debian
sudo apt install rust-analyzer

# macOS
brew install rust-analyzer

# Verify installation
which rust-analyzer
rust-analyzer --version
```

#### Issue: "Solidity language server not found"

**Solution**:
```bash
# Install globally
npm install -g @nomicfoundation/solidity-language-server

# Verify installation
which solidity-language-server
solidity-language-server --version

# If npm is not in PATH, add it:
export PATH="$PATH:$(npm root -g)/.bin"
```

#### Issue: "Language server starts but fails immediately"

**Possible Causes**:
1. Project root path issues
2. Invalid project configuration
3. Incompatible language server version
4. Resource constraints (memory, file descriptors)

**Solutions**:
- Verify project configuration in `.serena/project.yml`
- Check available system resources
- Update language server to latest version
- Reduce project size by excluding large directories in `.gitignore`

### Issue: "Unsupported file type"

**Solution**: Ensure you're analyzing .sol or .vy files. Other file types are not yet supported.

### Issue: "Invalid address format"

**Solution**: Ethereum addresses must be 42 characters (0x + 40 hex digits). Example: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1`

### Issue: "RPC endpoint not responding"

**Solution**: Check your RPC configuration in `web3_config.yml` or use a different endpoint.

### Issue: "API key required"

**Solution**: Some threat intelligence features require API keys. Add them to your configuration file.

## Contributing

We welcome contributions to enhance Web3 security analysis capabilities:

- Add new vulnerability patterns
- Integrate additional threat intelligence sources
- Improve detection accuracy
- Add support for more blockchain ecosystems

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## Resources

- [Solidity Security Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [OpenZeppelin Security Audits](https://www.openzeppelin.com/security-audits)
- [Ethereum Security Tools](https://ethereum.org/en/developers/docs/security/)
- [Web3 Threat Intelligence](https://cryptoscamdb.org/)

## License

Web3 analysis tools are part of Serena and licensed under the MIT License.
