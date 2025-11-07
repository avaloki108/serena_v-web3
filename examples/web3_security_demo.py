#!/usr/bin/env python3
"""
Example usage of Serena's Web3 vulnerability hunting tools.

This script demonstrates how to use the Web3 security analysis tools
for smart contract analysis, transaction inspection, DeFi protocol checking,
and threat intelligence lookups.
"""

import json
import sys
from pathlib import Path

# Add src to path for demonstration purposes
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def demo_smart_contract_analysis():
    """Demonstrate smart contract vulnerability analysis."""
    print("\n" + "=" * 80)
    print("DEMO 1: Smart Contract Vulnerability Analysis")
    print("=" * 80)

    # Example contract with vulnerabilities
    contract_code = '''
pragma solidity ^0.8.0;

contract Example {
    mapping(address => uint256) public balances;
    
    // Reentrancy vulnerability
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        msg.sender.call{value: amount}("");
        balances[msg.sender] = 0;
    }
    
    // Unprotected function
    function setAdmin(address newAdmin) public {
        // Missing access control
    }
    
    // tx.origin vulnerability
    function authenticate() public view returns (bool) {
        return tx.origin == msg.sender;
    }
}
'''

    print("\nContract to analyze:")
    print("-" * 80)
    print(contract_code.strip())
    print("-" * 80)

    print("\nVulnerabilities that would be detected:")
    print("  • Reentrancy: State change after external call")
    print("  • Unprotected Functions: Missing access control on setAdmin")
    print("  • tx.origin Usage: Should use msg.sender instead")
    print("  • Access Control: No access control mechanism")


def demo_transaction_analysis():
    """Demonstrate transaction security analysis."""
    print("\n" + "=" * 80)
    print("DEMO 2: Transaction Security Analysis")
    print("=" * 80)

    transaction_data = {
        "gas_limit": 6000000,
        "gas_price": 150,
        "calls": [
            {"method": "flashLoan", "amount": "1000 ETH", "target": "Aave"},
            {"method": "swap", "target": "Uniswap"},
            {"method": "swap", "target": "SushiSwap"},
            {"method": "repay", "target": "Aave"},
        ],
    }

    print("\nTransaction to analyze:")
    print("-" * 80)
    print(json.dumps(transaction_data, indent=2))
    print("-" * 80)

    print("\nSecurity concerns that would be detected:")
    print("  • Flash Loan: Transaction uses flash loan (high risk)")
    print("  • MEV: Multiple DEX swaps suggest possible sandwich attack")
    print("  • Unusual Gas: Gas limit of 6M is unusually high")
    print("  • Risk Score: 8/10 (HIGH)")


def demo_defi_protocol_check():
    """Demonstrate DeFi protocol security checking."""
    print("\n" + "=" * 80)
    print("DEMO 3: DeFi Protocol Security Check")
    print("=" * 80)

    protocol_config = {
        "protocol": "lending",
        "collateralFactor": 0.95,  # Very high - risky
        "oracle": "chainlink",
        "liquidation": None,  # Missing!
    }

    print("\nProtocol configuration to analyze:")
    print("-" * 80)
    print(json.dumps(protocol_config, indent=2))
    print("-" * 80)

    print("\nSecurity issues that would be detected:")
    print("  • High Collateral Factor: 0.95 is too high (medium risk)")
    print("  • Missing Liquidation: No liquidation mechanism (high risk)")
    print("  • Missing Pause: No emergency pause mechanism (medium risk)")
    print("  • Oracle Risk: Using oracle - needs multiple price feeds (high risk)")


def demo_threat_intelligence():
    """Demonstrate Web3 threat intelligence lookup."""
    print("\n" + "=" * 80)
    print("DEMO 4: Web3 Threat Intelligence")
    print("=" * 80)

    addresses = [
        ("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1", "Normal address"),
        ("0x000000000000000000000000000000000123abcd", "Vanity address"),
    ]

    for address, description in addresses:
        print(f"\nChecking: {address}")
        print(f"Type: {description}")
        print("-" * 80)

        if "00000000" in address:
            print("  ⚠️  Suspicious Pattern: Vanity address detected")
            print("     → Possible impersonation attempt")
            print("     → Threat Level: LOW")
        else:
            print("  ✓ No threats detected")
            print("     → Address appears safe")
            print("     → Threat Level: NONE")


def demo_web3_config():
    """Show example Web3 configuration."""
    print("\n" + "=" * 80)
    print("DEMO 5: Web3 Configuration Example")
    print("=" * 80)

    config_example = {
        "ethereum_rpc_url": "https://eth.llamarpc.com",
        "default_severity_threshold": "medium",
        "smart_contract_analysis": {
            "check_reentrancy": True,
            "check_overflow": True,
            "check_access_control": True,
        },
        "transaction_analysis": {
            "check_mev": True,
            "check_flash_loan": True,
            "high_gas_threshold": 1000000,
        },
        "threat_intel_sources": ["etherscan", "chainabuse", "cryptoscamdb"],
    }

    print("\nExample .serena/web3_config.yml:")
    print("-" * 80)
    print(json.dumps(config_example, indent=2))
    print("-" * 80)


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("Serena Web3 Vulnerability Hunting Tools - Usage Examples")
    print("=" * 80)
    print("\nThis demo shows what the Web3 security tools can detect.")
    print("In production, these tools integrate with Serena's MCP server")
    print("and can be used directly in Claude Code, Claude Desktop, etc.")

    demo_smart_contract_analysis()
    demo_transaction_analysis()
    demo_defi_protocol_check()
    demo_threat_intelligence()
    demo_web3_config()

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print("\nSerena's Web3 tools provide comprehensive security analysis:")
    print("  ✓ Smart Contract Analysis - 8+ vulnerability types")
    print("  ✓ Transaction Analysis - MEV, flash loans, suspicious calls")
    print("  ✓ DeFi Protocol Checks - Protocol-specific security issues")
    print("  ✓ Threat Intelligence - Address/contract reputation lookup")
    print("\nFor complete documentation, see: docs/web3_security.md")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
