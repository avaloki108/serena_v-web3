# @version ^0.3.0

"""
@title Simple Token
@license MIT
@author Test
@notice A simple ERC20-like token in Vyper
"""

from vyper.interfaces import ERC20

implements: ERC20

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

name: public(String[64])
symbol: public(String[32])
decimals: public(uint8)
totalSupply: public(uint256)

balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])

owner: public(address)

@external
def __init__(_name: String[64], _symbol: String[32], _supply: uint256):
    """
    @notice Contract constructor
    @param _name Token name
    @param _symbol Token symbol
    @param _supply Initial supply
    """
    self.name = _name
    self.symbol = _symbol
    self.decimals = 18
    self.totalSupply = _supply * 10 ** 18
    self.balanceOf[msg.sender] = self.totalSupply
    self.owner = msg.sender
    log Transfer(empty(address), msg.sender, self.totalSupply)

@external
def transfer(_to: address, _value: uint256) -> bool:
    """
    @notice Transfer tokens
    @param _to Recipient address
    @param _value Amount to transfer
    @return Success boolean
    """
    assert _to != empty(address), "Invalid recipient"
    assert self.balanceOf[msg.sender] >= _value, "Insufficient balance"
    
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    
    log Transfer(msg.sender, _to, _value)
    return True

@external
def approve(_spender: address, _value: uint256) -> bool:
    """
    @notice Approve spender to transfer tokens
    @param _spender Spender address
    @param _value Allowance amount
    @return Success boolean
    """
    assert _spender != empty(address), "Invalid spender"
    
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True

@external
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    """
    @notice Transfer tokens from one address to another
    @param _from Sender address
    @param _to Recipient address
    @param _value Amount to transfer
    @return Success boolean
    """
    assert _from != empty(address), "Invalid sender"
    assert _to != empty(address), "Invalid recipient"
    assert self.balanceOf[_from] >= _value, "Insufficient balance"
    assert self.allowance[_from][msg.sender] >= _value, "Insufficient allowance"
    
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    self.allowance[_from][msg.sender] -= _value
    
    log Transfer(_from, _to, _value)
    return True

@external
def mint(_to: address, _value: uint256):
    """
    @notice Mint new tokens (owner only)
    @param _to Recipient address
    @param _value Amount to mint
    """
    assert msg.sender == self.owner, "Only owner"
    assert _to != empty(address), "Invalid recipient"
    
    self.totalSupply += _value
    self.balanceOf[_to] += _value
    
    log Transfer(empty(address), _to, _value)

@external
def burn(_value: uint256):
    """
    @notice Burn tokens
    @param _value Amount to burn
    """
    assert self.balanceOf[msg.sender] >= _value, "Insufficient balance"
    
    self.balanceOf[msg.sender] -= _value
    self.totalSupply -= _value
    
    log Transfer(msg.sender, empty(address), _value)
