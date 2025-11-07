# Web3 Vulnerability Hunting - Implementation Architecture

## Overview

This document describes the architecture and implementation of Web3 vulnerability hunting capabilities added to the Serena agent toolkit.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Serena Agent                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              MCP Server Interface                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌────────────────────────┼────────────────────────────┐   │
│  │         Tool Registry  │                            │   │
│  │  ┌─────────────────────▼──────────────────────┐     │   │
│  │  │         Web3 Security Tools                │     │   │
│  │  │  ┌──────────────────────────────────────┐  │     │   │
│  │  │  │ AnalyzeSmartContractTool             │  │     │   │
│  │  │  │  - Reentrancy detection              │  │     │   │
│  │  │  │  - Overflow checking                 │  │     │   │
│  │  │  │  - Access control validation         │  │     │   │
│  │  │  │  - tx.origin detection               │  │     │   │
│  │  │  │  - Delegatecall warnings             │  │     │   │
│  │  │  │  - Timestamp dependence              │  │     │   │
│  │  │  │  - Unchecked calls                   │  │     │   │
│  │  │  └──────────────────────────────────────┘  │     │   │
│  │  │  ┌──────────────────────────────────────┐  │     │   │
│  │  │  │ AnalyzeTransactionTool               │  │     │   │
│  │  │  │  - MEV pattern detection             │  │     │   │
│  │  │  │  - Flash loan identification         │  │     │   │
│  │  │  │  - Gas usage analysis                │  │     │   │
│  │  │  │  - Suspicious call detection         │  │     │   │
│  │  │  │  - Token approval validation         │  │     │   │
│  │  │  └──────────────────────────────────────┘  │     │   │
│  │  │  ┌──────────────────────────────────────┐  │     │   │
│  │  │  │ CheckDeFiProtocolTool                │  │     │   │
│  │  │  │  - Lending protocol checks           │  │     │   │
│  │  │  │  - DEX security validation           │  │     │   │
│  │  │  │  - Staking mechanism analysis        │  │     │   │
│  │  │  │  - Yield farming security            │  │     │   │
│  │  │  └──────────────────────────────────────┘  │     │   │
│  │  │  ┌──────────────────────────────────────┐  │     │   │
│  │  │  │ Web3ThreatIntelligenceTool           │  │     │   │
│  │  │  │  - Address reputation checking       │  │     │   │
│  │  │  │  - Scam database integration         │  │     │   │
│  │  │  │  - Phishing detection                │  │     │   │
│  │  │  │  - Sanctions list checking           │  │     │   │
│  │  │  └──────────────────────────────────────┘  │     │   │
│  │  └─────────────────────────────────────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                 │
│  ┌────────────────────────▼────────────────────────────┐   │
│  │         Configuration Management                    │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │ Web3Config                                   │  │   │
│  │  │  - RPC endpoints                             │  │   │
│  │  │  - API keys                                  │  │   │
│  │  │  - Security thresholds                       │  │   │
│  │  │  - Check configurations                      │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. AnalyzeSmartContractTool

**Purpose:** Static analysis of smart contract code for security vulnerabilities

**Input:**
- `relative_path`: Path to smart contract file (.sol or .vy)
- `vulnerability_types`: List of specific checks to perform
- `severity_threshold`: Minimum severity to report (low/medium/high/critical)

**Output:** JSON with detected vulnerabilities, severity levels, and recommendations

**Implementation Details:**
- Pattern-based detection using regex and AST analysis
- Solidity-specific checks for versions < 0.8.0 (overflow issues)
- Context-aware analysis (checks surrounding code patterns)
- Extensible architecture for adding new vulnerability types

**Detected Vulnerabilities:**
1. **Reentrancy**: External calls before state changes
2. **Overflow**: Arithmetic without SafeMath in old Solidity
3. **Unprotected Functions**: Public/external functions without modifiers
4. **tx.origin**: Usage for authentication
5. **Delegatecall**: Unsafe delegatecall usage
6. **Timestamp Dependence**: Reliance on block.timestamp
7. **Unchecked Calls**: .call() and .send() without checking returns
8. **Access Control**: Missing ownership/permission patterns

### 2. AnalyzeTransactionTool

**Purpose:** Runtime analysis of blockchain transactions for suspicious activity

**Input:**
- `transaction_hash`: On-chain transaction hash (optional)
- `transaction_data`: Pre-broadcast transaction data (optional)
- `check_types`: Specific security checks to perform

**Output:** JSON with risk score, findings, and severity levels

**Implementation Details:**
- Pattern matching on transaction call data
- Gas usage analysis and anomaly detection
- Multi-factor risk scoring algorithm
- Extensible check system

**Detected Patterns:**
1. **MEV**: Multiple DEX interactions, high gas prices
2. **Flash Loans**: Borrow-action-repay patterns
3. **Unusual Gas**: Abnormally high gas limits/prices
4. **Suspicious Calls**: selfdestruct, delegatecall in transactions
5. **Token Approvals**: Unlimited approval detection

### 3. CheckDeFiProtocolTool

**Purpose:** Protocol-level security analysis for DeFi applications

**Input:**
- `protocol_config_path`: Path to protocol configuration file
- `protocol_type`: Type of protocol (lending/dex/staking/yield_farming)

**Output:** JSON with protocol-specific findings and recommendations

**Implementation Details:**
- Protocol-type specific checkers
- Configuration validation
- Best practice verification
- Common DeFi vulnerability detection

**Protocol-Specific Checks:**

**Lending:**
- Oracle manipulation risks
- Liquidation mechanism validation
- Collateral factor analysis
- Reserve factor checks

**DEX:**
- Slippage protection
- MEV protection mechanisms
- Liquidity risks
- Impermanent loss considerations

**Staking:**
- Lock period configuration
- Reward rate sustainability
- Economic attack vectors
- Withdrawal mechanisms

**Yield Farming:**
- Impermanent loss warnings
- APY sustainability
- Strategy risk assessment

### 4. Web3ThreatIntelligenceTool

**Purpose:** Address and contract reputation checking against threat databases

**Input:**
- `address`: Ethereum address (0x...)
- `check_type`: Type of threat intel check (all/scam/phishing/hack/sanctions)

**Output:** JSON with threat level, findings, and recommendations

**Implementation Details:**
- Address pattern analysis
- Integration framework for threat intel APIs
- Multi-source threat aggregation
- Threat level calculation

**Threat Sources:**
- Etherscan
- ChainAbuse
- CryptoScamDB
- BlockSec
- OFAC sanctions lists

## Configuration System

### Web3Config Dataclass

```python
@dataclass
class Web3Config:
    # RPC Endpoints
    ethereum_rpc_url: str
    polygon_rpc_url: str
    bsc_rpc_url: str
    arbitrum_rpc_url: str
    optimism_rpc_url: str
    
    # API Keys
    etherscan_api_key: str
    blocksec_api_key: str
    chainanalysis_api_key: str
    
    # Analysis Settings
    default_severity_threshold: str
    max_transaction_lookback: int
    enable_threat_intelligence: bool
    
    # Check Configurations
    smart_contract_analysis: dict
    defi_protocol_checks: dict
    transaction_analysis: dict
    threat_intel_sources: list
```

### Configuration Loading Priority

1. Environment variables (highest priority)
2. Project-specific `.serena/web3_config.yml`
3. User config `~/.serena/web3_config.yml`
4. Default values (lowest priority)

## Integration with Serena

### Tool Registration

Tools are automatically discovered and registered through:

```python
# src/serena/tools/__init__.py
from .web3_tools import *
```

### MCP Server Integration

Tools expose MCP-compatible interfaces:
- Tool name derived from class name (snake_case)
- Apply method parameters become tool parameters
- Docstrings provide tool descriptions
- Type hints enable parameter validation

### Usage in Claude Code/Desktop

```
User: "Analyze the smart contract at contracts/Token.sol"
↓
Claude calls: analyze_smart_contract(
    relative_path="contracts/Token.sol",
    severity_threshold="medium"
)
↓
Tool executes analysis
↓
Claude receives JSON results
↓
Claude summarizes findings for user
```

## Testing Strategy

### Test Structure

```
test/serena/test_web3_tools.py
├── TestAnalyzeSmartContractTool
│   ├── test_analyze_solidity_contract_reentrancy
│   ├── test_analyze_solidity_contract_overflow
│   ├── test_analyze_unprotected_functions
│   ├── test_analyze_tx_origin_vulnerability
│   ├── test_analyze_delegatecall_vulnerability
│   ├── test_severity_threshold_filtering
│   └── test_unsupported_file_type
├── TestAnalyzeTransactionTool
│   ├── test_analyze_transaction_mev_pattern
│   ├── test_analyze_flash_loan_detection
│   ├── test_analyze_unusual_gas
│   ├── test_analyze_suspicious_calls
│   ├── test_analyze_token_approval
│   ├── test_risk_level_calculation
│   └── test_missing_transaction_data_error
├── TestCheckDeFiProtocolTool
│   ├── test_check_lending_protocol
│   ├── test_check_dex_protocol
│   ├── test_check_staking_protocol
│   └── test_check_common_defi_issues
└── TestWeb3ThreatIntelligenceTool
    ├── test_check_valid_address_format
    ├── test_check_invalid_address_format
    ├── test_check_suspicious_patterns
    ├── test_threat_levels
    └── test_check_type_filtering
```

### Test Fixtures

- `agent_with_temp_project`: Temporary Serena project for testing
- `test/resources/contracts/VulnerableExample.sol`: Sample vulnerable contract
- `test/resources/defi/lending_protocol.json`: Sample DeFi configuration

## Performance Considerations

### Static Analysis Performance

- Pattern-based detection: O(n) where n = lines of code
- Caching disabled by default (each analysis is independent)
- Large contracts (>10k LOC) may take 1-2 seconds

### Transaction Analysis Performance

- Pattern matching: O(m) where m = number of calls
- Risk calculation: O(1)
- Typically completes in <100ms

### Optimization Strategies

1. **Caching**: Enable for repeated analyses (configurable)
2. **Parallel Processing**: Analyze multiple files concurrently
3. **Incremental Analysis**: Only re-analyze changed files
4. **Smart Filtering**: Skip irrelevant checks based on context

## Security Considerations

### False Positives

- Pattern-based detection may flag legitimate code
- Users should review all findings
- Severity levels help prioritize review

### False Negatives

- Not all vulnerabilities can be detected statically
- Complex attack vectors may be missed
- Formal verification recommended for critical contracts

### Privacy

- No data sent to external services by default
- Threat intelligence features require explicit API configuration
- All analysis runs locally

## Extension Points

### Adding New Vulnerability Types

```python
class AnalyzeSmartContractTool(Tool):
    def _check_custom_vulnerability(self, content: str) -> list[dict]:
        # Custom detection logic
        vulnerabilities = []
        # ... analyze content ...
        return vulnerabilities
```

### Adding Threat Intelligence Sources

```python
class Web3ThreatIntelligenceTool(Tool):
    def _check_custom_database(self, address: str) -> list[dict]:
        # Integration with custom threat intel API
        findings = []
        # ... query API ...
        return findings
```

### Custom Protocol Checks

```python
class CheckDeFiProtocolTool(Tool):
    def _check_custom_protocol(self, content: str) -> list[dict]:
        # Protocol-specific security checks
        findings = []
        # ... analyze protocol config ...
        return findings
```

## Future Enhancements

### Planned Features

1. **Dynamic Analysis**: Transaction simulation and fuzzing
2. **Machine Learning**: AI-powered vulnerability detection
3. **Real-time Monitoring**: Continuous contract monitoring
4. **Formal Verification**: Integration with Certora, K Framework
5. **Multi-chain Support**: Extended blockchain coverage
6. **Gas Optimization**: Identify expensive operations
7. **Audit Reports**: Generate professional audit documents
8. **Integration APIs**: Connect to security platforms

### Community Contributions

Areas open for contribution:
- New vulnerability patterns
- Additional blockchain support
- Threat intelligence integrations
- Performance optimizations
- Documentation improvements

## References

- [Solidity Security Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [SWC Registry](https://swcregistry.io/)
- [DeFi Security Framework](https://github.com/dedaub/defi-security)
- [Ethereum Security Tools](https://ethereum.org/en/developers/docs/security/)
- [Web3 Security Library](https://github.com/CoinFabrik/web3-security-library)

## Changelog

### v1.0.0 (Initial Release)
- Smart contract analysis with 8 vulnerability types
- Transaction security analysis
- DeFi protocol checking
- Threat intelligence integration
- Comprehensive test suite
- Full documentation
