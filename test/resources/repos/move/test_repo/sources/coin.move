/// Simple coin module for Move
module test_coin::coin {
    use std::signer;
    use std::error;
    use aptos_framework::coin::{Self, Coin, MintCapability, BurnCapability};
    
    /// Error codes
    const ENOT_ADMIN: u64 = 1;
    const EINSUFFICIENT_BALANCE: u64 = 2;
    
    /// Coin type for TestCoin
    struct TestCoin has key {}
    
    /// Capabilities for minting and burning
    struct Capabilities has key {
        mint_cap: MintCapability<TestCoin>,
        burn_cap: BurnCapability<TestCoin>,
    }
    
    /// Initialize the coin
    public entry fun initialize(
        account: &signer,
        name: vector<u8>,
        symbol: vector<u8>,
        decimals: u8,
    ) {
        let (burn_cap, freeze_cap, mint_cap) = coin::initialize<TestCoin>(
            account,
            string::utf8(name),
            string::utf8(symbol),
            decimals,
            true,
        );
        
        coin::destroy_freeze_cap(freeze_cap);
        
        move_to(account, Capabilities {
            mint_cap,
            burn_cap,
        });
    }
    
    /// Mint new coins
    public entry fun mint(
        admin: &signer,
        recipient: address,
        amount: u64,
    ) acquires Capabilities {
        let admin_addr = signer::address_of(admin);
        assert!(exists<Capabilities>(admin_addr), error::not_found(ENOT_ADMIN));
        
        let caps = borrow_global<Capabilities>(admin_addr);
        let coins = coin::mint<TestCoin>(amount, &caps.mint_cap);
        coin::deposit(recipient, coins);
    }
    
    /// Burn coins
    public entry fun burn(
        account: &signer,
        amount: u64,
    ) acquires Capabilities {
        let account_addr = signer::address_of(account);
        let caps = borrow_global<Capabilities>(account_addr);
        let coins = coin::withdraw<TestCoin>(account, amount);
        coin::burn(coins, &caps.burn_cap);
    }
    
    /// Transfer coins
    public entry fun transfer(
        from: &signer,
        to: address,
        amount: u64,
    ) {
        coin::transfer<TestCoin>(from, to, amount);
    }
    
    /// Get balance
    public fun balance(account: address): u64 {
        coin::balance<TestCoin>(account)
    }
    
    #[test_only]
    use std::string;
    
    #[test(admin = @0x1)]
    fun test_init(admin: signer) {
        initialize(&admin, b"Test Coin", b"TEST", 8);
        assert!(exists<Capabilities>(signer::address_of(&admin)), 0);
    }
}
