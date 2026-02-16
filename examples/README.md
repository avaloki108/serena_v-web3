# Serena Examples

This directory contains example scripts demonstrating Serena's capabilities.

## Web3 Security Demo

**File:** `web3_security_demo.py`

An interactive demonstration of Serena's Web3 vulnerability hunting tools.

### Running the Demo

```bash
python3 examples/web3_security_demo.py
```

### What It Demonstrates

1. **Smart Contract Analysis**
   - Detection of reentrancy vulnerabilities
   - Identification of unprotected functions
   - tx.origin usage warnings
   - Access control issues

2. **Transaction Analysis**
   - MEV (Maximal Extractable Value) detection
   - Flash loan attack patterns
   - Unusual gas usage
   - Risk scoring

3. **DeFi Protocol Checks**
   - Lending protocol security
   - Collateral factor validation
   - Missing safety mechanisms
   - Oracle manipulation risks

4. **Threat Intelligence**
   - Address reputation checking
   - Vanity address detection
   - Suspicious pattern identification

5. **Configuration Examples**
   - RPC endpoint setup
   - Security threshold configuration
   - Threat intelligence source integration

### Output

The demo script produces formatted output showing:
- Example vulnerable code
- Security issues that would be detected
- Risk levels and recommendations
- Configuration examples

### Next Steps

After reviewing the demo, see the full documentation:
- [Web3 Security Guide](../docs/web3_security.md)
- [Main README](../README.md)

### Using in Production

To use these tools in your own projects:

1. Activate Serena in your project directory
2. Configure Web3 settings in `.serena/web3_config.yml`
3. Use the tools via:
   - Serena MCP server with Claude Code/Desktop
   - Python API in custom agents
   - Command-line interface

Example:
```python
from serena.agent import SerenaAgent
from serena.tools.web3_tools import AnalyzeSmartContractTool

agent = SerenaAgent(project="/path/to/project")
tool = AnalyzeSmartContractTool(agent)
result = tool.apply("contracts/MyToken.sol")
```
