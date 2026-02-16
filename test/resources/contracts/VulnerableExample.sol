// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * Example smart contract with intentional vulnerabilities for testing
 * the Web3 security analysis tools.
 * 
 * WARNING: This contract is for testing purposes only. DO NOT deploy to mainnet.
 */
contract VulnerableExample {
    mapping(address => uint256) public balances;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Vulnerability: Reentrancy
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] = 0;  // State change after external call
    }
    
    // Vulnerability: Unprotected function
    function setOwner(address newOwner) public {
        owner = newOwner;  // Anyone can change owner
    }
    
    // Vulnerability: tx.origin for authentication
    function isOwner() public view returns (bool) {
        return tx.origin == owner;  // Should use msg.sender
    }
    
    // Vulnerability: Unchecked external call
    function transfer(address payable recipient, uint256 amount) public {
        recipient.send(amount);  // Return value not checked
    }
    
    // Vulnerability: Timestamp dependence
    function timeBasedLottery() public payable {
        require(msg.value > 0, "Must send ETH");
        if (block.timestamp % 2 == 0) {
            payable(msg.sender).transfer(address(this).balance);
        }
    }
    
    receive() external payable {
        balances[msg.sender] += msg.value;
    }
}
