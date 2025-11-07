use starknet::ContractAddress;

#[starknet::interface]
trait ISimpleToken<TContractState> {
    fn get_name(self: @TContractState) -> felt252;
    fn get_symbol(self: @TContractState) -> felt252;
    fn get_decimals(self: @TContractState) -> u8;
    fn get_total_supply(self: @TContractState) -> u256;
    fn balance_of(self: @TContractState, account: ContractAddress) -> u256;
    fn allowance(self: @TContractState, owner: ContractAddress, spender: ContractAddress) -> u256;
    fn transfer(ref self: TContractState, recipient: ContractAddress, amount: u256) -> bool;
    fn transfer_from(ref self: TContractState, sender: ContractAddress, recipient: ContractAddress, amount: u256) -> bool;
    fn approve(ref self: TContractState, spender: ContractAddress, amount: u256) -> bool;
    fn mint(ref self: TContractState, recipient: ContractAddress, amount: u256);
    fn burn(ref self: TContractState, amount: u256);
}

#[starknet::contract]
mod SimpleToken {
    use starknet::{ContractAddress, get_caller_address};
    use starknet::storage::{Map, StorageMapReadAccess, StorageMapWriteAccess};
    
    #[storage]
    struct Storage {
        name: felt252,
        symbol: felt252,
        decimals: u8,
        total_supply: u256,
        balances: Map<ContractAddress, u256>,
        allowances: Map<(ContractAddress, ContractAddress), u256>,
        owner: ContractAddress,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        Transfer: Transfer,
        Approval: Approval,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Transfer {
        from: ContractAddress,
        to: ContractAddress,
        value: u256,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Approval {
        owner: ContractAddress,
        spender: ContractAddress,
        value: u256,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        name: felt252,
        symbol: felt252,
        initial_supply: u256,
    ) {
        self.name.write(name);
        self.symbol.write(symbol);
        self.decimals.write(18);
        
        let caller = get_caller_address();
        self.owner.write(caller);
        self.total_supply.write(initial_supply);
        self.balances.write(caller, initial_supply);
        
        self.emit(Transfer {
            from: starknet::contract_address_const::<0>(),
            to: caller,
            value: initial_supply,
        });
    }
    
    #[abi(embed_v0)]
    impl SimpleTokenImpl of super::ISimpleToken<ContractState> {
        fn get_name(self: @ContractState) -> felt252 {
            self.name.read()
        }
        
        fn get_symbol(self: @ContractState) -> felt252 {
            self.symbol.read()
        }
        
        fn get_decimals(self: @ContractState) -> u8 {
            self.decimals.read()
        }
        
        fn get_total_supply(self: @ContractState) -> u256 {
            self.total_supply.read()
        }
        
        fn balance_of(self: @ContractState, account: ContractAddress) -> u256 {
            self.balances.read(account)
        }
        
        fn allowance(self: @ContractState, owner: ContractAddress, spender: ContractAddress) -> u256 {
            self.allowances.read((owner, spender))
        }
        
        fn transfer(ref self: ContractState, recipient: ContractAddress, amount: u256) -> bool {
            let caller = get_caller_address();
            self._transfer(caller, recipient, amount);
            true
        }
        
        fn transfer_from(
            ref self: ContractState,
            sender: ContractAddress,
            recipient: ContractAddress,
            amount: u256
        ) -> bool {
            let caller = get_caller_address();
            let current_allowance = self.allowances.read((sender, caller));
            assert(current_allowance >= amount, 'Insufficient allowance');
            
            self.allowances.write((sender, caller), current_allowance - amount);
            self._transfer(sender, recipient, amount);
            true
        }
        
        fn approve(ref self: ContractState, spender: ContractAddress, amount: u256) -> bool {
            let caller = get_caller_address();
            self.allowances.write((caller, spender), amount);
            
            self.emit(Approval {
                owner: caller,
                spender: spender,
                value: amount,
            });
            true
        }
        
        fn mint(ref self: ContractState, recipient: ContractAddress, amount: u256) {
            let caller = get_caller_address();
            assert(caller == self.owner.read(), 'Only owner can mint');
            
            let new_supply = self.total_supply.read() + amount;
            self.total_supply.write(new_supply);
            
            let new_balance = self.balances.read(recipient) + amount;
            self.balances.write(recipient, new_balance);
            
            self.emit(Transfer {
                from: starknet::contract_address_const::<0>(),
                to: recipient,
                value: amount,
            });
        }
        
        fn burn(ref self: ContractState, amount: u256) {
            let caller = get_caller_address();
            let balance = self.balances.read(caller);
            assert(balance >= amount, 'Insufficient balance');
            
            self.balances.write(caller, balance - amount);
            self.total_supply.write(self.total_supply.read() - amount);
            
            self.emit(Transfer {
                from: caller,
                to: starknet::contract_address_const::<0>(),
                value: amount,
            });
        }
    }
    
    #[generate_trait]
    impl InternalFunctions of InternalFunctionsTrait {
        fn _transfer(
            ref self: ContractState,
            sender: ContractAddress,
            recipient: ContractAddress,
            amount: u256
        ) {
            let sender_balance = self.balances.read(sender);
            assert(sender_balance >= amount, 'Insufficient balance');
            
            self.balances.write(sender, sender_balance - amount);
            let recipient_balance = self.balances.read(recipient);
            self.balances.write(recipient, recipient_balance + amount);
            
            self.emit(Transfer {
                from: sender,
                to: recipient,
                value: amount,
            });
        }
    }
}
