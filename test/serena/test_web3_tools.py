"""
Tests for Web3 vulnerability hunting tools.
"""

import json
import tempfile
from pathlib import Path

import pytest

from serena.agent import SerenaAgent
from serena.tools.web3_tools import (
    AnalyzeDeFiProtocolTool,
    AnalyzeSmartContractTool,
    AnalyzeTransactionTool,
    Web3ThreatIntelligenceTool,
)


@pytest.fixture
def agent_with_temp_project():
    """Create a SerenaAgent with a temporary project."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple project structure
        project_path = Path(temp_dir)
        (project_path / ".serena").mkdir()

        agent = SerenaAgent(project=str(project_path))
        yield agent, project_path


class TestAnalyzeSmartContractTool:
    """Tests for smart contract analysis tool."""

    def test_analyze_solidity_contract_reentrancy(self, agent_with_temp_project):
        """Test detection of reentrancy vulnerability."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeSmartContractTool(agent)

        # Create a vulnerable contract
        contract_content = """
pragma solidity ^0.8.0;

contract Vulnerable {
    mapping(address => uint256) public balances;

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] = 0;  // State change after external call
    }
}
"""
        contract_path = project_path / "Vulnerable.sol"
        contract_path.write_text(contract_content)

        result_json = tool.apply("Vulnerable.sol")
        result = json.loads(result_json)

        assert result["file"] == "Vulnerable.sol"
        assert result["vulnerabilities_found"] > 0
        assert any(v["type"] == "reentrancy" for v in result["vulnerabilities"])

    def test_analyze_solidity_contract_overflow(self, agent_with_temp_project):
        """Test detection of overflow vulnerability."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeSmartContractTool(agent)

        # Create a contract with overflow risk
        contract_content = """
pragma solidity ^0.7.6;

contract OldContract {
    uint256 public total;

    function add(uint256 value) public {
        total = total + value;  // No SafeMath, old Solidity version
    }
}
"""
        contract_path = project_path / "OldContract.sol"
        contract_path.write_text(contract_content)

        result_json = tool.apply("OldContract.sol")
        result = json.loads(result_json)

        assert result["file"] == "OldContract.sol"
        assert result["vulnerabilities_found"] > 0
        # Should detect overflow risk in old Solidity version

    def test_analyze_unprotected_functions(self, agent_with_temp_project):
        """Test detection of unprotected functions."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeSmartContractTool(agent)

        contract_content = """
pragma solidity ^0.8.0;

contract Unprotected {
    address public owner;

    function setOwner(address newOwner) public {
        owner = newOwner;
    }
}
"""
        contract_path = project_path / "Unprotected.sol"
        contract_path.write_text(contract_content)

        result_json = tool.apply("Unprotected.sol")
        result = json.loads(result_json)

        assert result["file"] == "Unprotected.sol"
        assert result["vulnerabilities_found"] > 0
        assert any(v["type"] == "unprotected_functions" for v in result["vulnerabilities"])

    def test_analyze_tx_origin_vulnerability(self, agent_with_temp_project):
        """Test detection of tx.origin usage."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeSmartContractTool(agent)

        contract_content = """
pragma solidity ^0.8.0;

contract TxOriginAuth {
    address public owner;

    function isOwner() public view returns (bool) {
        return tx.origin == owner;
    }
}
"""
        contract_path = project_path / "TxOriginAuth.sol"
        contract_path.write_text(contract_content)

        result_json = tool.apply("TxOriginAuth.sol")
        result = json.loads(result_json)

        assert result["vulnerabilities_found"] > 0
        assert any(v["type"] == "tx_origin" for v in result["vulnerabilities"])

    def test_analyze_delegatecall_vulnerability(self, agent_with_temp_project):
        """Test detection of unsafe delegatecall."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeSmartContractTool(agent)

        contract_content = """
pragma solidity ^0.8.0;

contract DelegateCall {
    function execute(address target, bytes memory data) public {
        target.delegatecall(data);
    }
}
"""
        contract_path = project_path / "DelegateCall.sol"
        contract_path.write_text(contract_content)

        result_json = tool.apply("DelegateCall.sol")
        result = json.loads(result_json)

        assert result["vulnerabilities_found"] > 0
        assert any(v["type"] == "delegatecall" and v["severity"] == "critical" for v in result["vulnerabilities"])

    def test_severity_threshold_filtering(self, agent_with_temp_project):
        """Test that severity threshold filters results correctly."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeSmartContractTool(agent)

        contract_content = """
pragma solidity ^0.8.0;

contract Mixed {
    function transfer() public {
        msg.sender.call{value: 1}("");  // High severity
    }
}
"""
        contract_path = project_path / "Mixed.sol"
        contract_path.write_text(contract_content)

        # Test with high severity threshold
        result_json = tool.apply("Mixed.sol", severity_threshold="high")
        result = json.loads(result_json)

        # Should only return high/critical severity issues
        for vuln in result["vulnerabilities"]:
            assert vuln["severity"] in ["high", "critical"]

    def test_unsupported_file_type(self, agent_with_temp_project):
        """Test handling of unsupported file types."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeSmartContractTool(agent)

        # Create a non-contract file
        file_path = project_path / "script.js"
        file_path.write_text("console.log('test');")

        result_json = tool.apply("script.js")
        result = json.loads(result_json)

        assert "error" in result
        assert "Unsupported file type" in result["error"]


class TestAnalyzeTransactionTool:
    """Tests for transaction analysis tool."""

    def test_analyze_transaction_mev_pattern(self, agent_with_temp_project):
        """Test detection of MEV patterns."""
        agent, _ = agent_with_temp_project
        tool = AnalyzeTransactionTool(agent)

        tx_data = {
            "gas_price": 150,
            "gas_limit": 300000,
            "calls": [
                {"method": "swap", "target": "uniswap"},
                {"method": "swap", "target": "sushiswap"},
                {"method": "swap", "target": "uniswap"},
            ],
        }

        result_json = tool.apply(transaction_data=tx_data, check_types=["mev"])
        result = json.loads(result_json)

        assert result["risk_score"] > 0
        assert any(f["type"] == "mev" for f in result["findings"])

    def test_analyze_flash_loan_detection(self, agent_with_temp_project):
        """Test detection of flash loan patterns."""
        agent, _ = agent_with_temp_project
        tool = AnalyzeTransactionTool(agent)

        tx_data = {
            "calls": [
                {"method": "flashLoan", "target": "aave"},
                {"method": "swap", "target": "uniswap"},
                {"method": "repay", "target": "aave"},
            ]
        }

        result_json = tool.apply(transaction_data=tx_data, check_types=["flash_loan"])
        result = json.loads(result_json)

        assert result["risk_score"] > 0
        assert any(f["type"] == "flash_loan" for f in result["findings"])
        assert result["risk_level"] in ["medium", "high", "critical"]

    def test_analyze_unusual_gas(self, agent_with_temp_project):
        """Test detection of unusual gas usage."""
        agent, _ = agent_with_temp_project
        tool = AnalyzeTransactionTool(agent)

        tx_data = {"gas_limit": 6000000, "gas_price": 50}

        result_json = tool.apply(transaction_data=tx_data, check_types=["unusual_gas"])
        result = json.loads(result_json)

        assert any(f["type"] == "unusual_gas" for f in result["findings"])

    def test_analyze_suspicious_calls(self, agent_with_temp_project):
        """Test detection of suspicious contract calls."""
        agent, _ = agent_with_temp_project
        tool = AnalyzeTransactionTool(agent)

        tx_data = {"calls": [{"method": "selfdestruct", "target": "0x123"}]}

        result_json = tool.apply(transaction_data=tx_data, check_types=["suspicious_calls"])
        result = json.loads(result_json)

        assert any(f["type"] == "suspicious_calls" and f["severity"] == "critical" for f in result["findings"])

    def test_analyze_token_approval(self, agent_with_temp_project):
        """Test detection of risky token approvals."""
        agent, _ = agent_with_temp_project
        tool = AnalyzeTransactionTool(agent)

        tx_data = {"calls": [{"method": "approve", "amount": "0xffffffffffffffff"}]}

        result_json = tool.apply(transaction_data=tx_data, check_types=["token_approval"])
        result = json.loads(result_json)

        assert any(f["type"] == "token_approval" for f in result["findings"])

    def test_risk_level_calculation(self, agent_with_temp_project):
        """Test that risk level is calculated correctly."""
        agent, _ = agent_with_temp_project
        tool = AnalyzeTransactionTool(agent)

        # High risk transaction
        high_risk_tx = {
            "gas_limit": 7000000,
            "calls": [
                {"method": "delegatecall", "target": "0x123"},
                {"method": "selfdestruct", "target": "0x456"},
            ],
        }

        result_json = tool.apply(transaction_data=high_risk_tx)
        result = json.loads(result_json)

        assert result["risk_level"] in ["high", "critical"]
        assert result["risk_score"] >= 5

    def test_missing_transaction_data_error(self, agent_with_temp_project):
        """Test error handling when no transaction data provided."""
        agent, _ = agent_with_temp_project
        tool = AnalyzeTransactionTool(agent)

        result_json = tool.apply()
        result = json.loads(result_json)

        assert "error" in result


class TestCheckDeFiProtocolTool:
    """Tests for DeFi protocol checking tool."""

    def test_check_lending_protocol(self, agent_with_temp_project):
        """Test lending protocol security checks."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeDeFiProtocolTool(agent)

        config_content = """
{
    "protocol": "lending",
    "oracle": "chainlink",
    "collateralFactor": 0.95,
    "liquidationIncentive": 1.08
}
"""
        config_path = project_path / "lending_config.json"
        config_path.write_text(config_content)

        result_json = tool.apply("lending_config.json", protocol_type="lending")
        result = json.loads(result_json)

        assert result["protocol_type"] == "lending"
        assert result["total_findings"] > 0
        # Should detect high collateral factor
        assert any(f["type"] == "high_collateral_factor" for f in result["findings"])

    def test_check_dex_protocol(self, agent_with_temp_project):
        """Test DEX protocol security checks."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeDeFiProtocolTool(agent)

        config_content = """
{
    "protocol": "dex",
    "swapFee": 0.003
}
"""
        config_path = project_path / "dex_config.json"
        config_path.write_text(config_content)

        result_json = tool.apply("dex_config.json", protocol_type="dex")
        result = json.loads(result_json)

        # Should detect missing slippage protection
        assert any(f["type"] == "missing_slippage" for f in result["findings"])

    def test_check_staking_protocol(self, agent_with_temp_project):
        """Test staking protocol security checks."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeDeFiProtocolTool(agent)

        config_content = """
{
    "protocol": "staking",
    "rewardRate": 150.0
}
"""
        config_path = project_path / "staking_config.json"
        config_path.write_text(config_content)

        result_json = tool.apply("staking_config.json", protocol_type="staking")
        result = json.loads(result_json)

        # Should detect high reward rate
        assert any(f["type"] == "high_reward_rate" and f["severity"] == "high" for f in result["findings"])

    def test_check_common_defi_issues(self, agent_with_temp_project):
        """Test common DeFi security issues detection."""
        agent, project_path = agent_with_temp_project
        tool = AnalyzeDeFiProtocolTool(agent)

        config_content = """
{
    "protocol": "lending"
}
"""
        config_path = project_path / "minimal_config.json"
        config_path.write_text(config_content)

        result_json = tool.apply("minimal_config.json", protocol_type="lending")
        result = json.loads(result_json)

        # Should detect missing pause mechanism
        assert any(f["type"] == "missing_pause" for f in result["findings"])
        # Should detect missing access control
        assert any(f["type"] == "missing_access_control" for f in result["findings"])


class TestWeb3ThreatIntelligenceTool:
    """Tests for Web3 threat intelligence tool."""

    def test_check_valid_address_format(self, agent_with_temp_project):
        """Test validation of Ethereum address format."""
        agent, _ = agent_with_temp_project
        tool = Web3ThreatIntelligenceTool(agent)

        result_json = tool.apply("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
        result = json.loads(result_json)

        assert "error" not in result
        assert result["address"].startswith("0x")

    def test_check_invalid_address_format(self, agent_with_temp_project):
        """Test error handling for invalid address format."""
        agent, _ = agent_with_temp_project
        tool = Web3ThreatIntelligenceTool(agent)

        result_json = tool.apply("invalid_address")
        result = json.loads(result_json)

        assert "error" in result
        assert "Invalid address format" in result["error"]

    def test_check_suspicious_patterns(self, agent_with_temp_project):
        """Test detection of suspicious address patterns."""
        agent, _ = agent_with_temp_project
        tool = Web3ThreatIntelligenceTool(agent)

        # Vanity address with many leading zeros
        vanity_address = "0x" + "0" * 10 + "a" * 30

        result_json = tool.apply(vanity_address)
        result = json.loads(result_json)

        assert any(f["type"] == "suspicious_pattern" for f in result["findings"])

    def test_threat_levels(self, agent_with_temp_project):
        """Test that threat levels are assigned correctly."""
        agent, _ = agent_with_temp_project
        tool = Web3ThreatIntelligenceTool(agent)

        # Normal address
        normal_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"

        result_json = tool.apply(normal_address)
        result = json.loads(result_json)

        assert result["threat_level"] in ["none", "low", "medium", "high", "critical"]
        assert "recommendation" in result

    def test_check_type_filtering(self, agent_with_temp_project):
        """Test that check_type parameter filters checks correctly."""
        agent, _ = agent_with_temp_project
        tool = Web3ThreatIntelligenceTool(agent)

        address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"

        result_json = tool.apply(address, check_type="scam")
        result = json.loads(result_json)

        assert result["checked_types"] == "scam"
