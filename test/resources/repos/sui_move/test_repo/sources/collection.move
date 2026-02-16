/// Simple NFT collection module for Sui Move
module sui_nft::collection {
    use sui::object::{Self, UID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};
    use std::string::{Self, String};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::event;
    
    /// NFT object
    struct NFT has key, store {
        id: UID,
        name: String,
        description: String,
        url: String,
        creator: address,
    }
    
    /// Collection info
    struct Collection has key {
        id: UID,
        name: String,
        description: String,
        creator: address,
        total_supply: u64,
    }
    
    /// Events
    struct NFTMinted has copy, drop {
        nft_id: address,
        creator: address,
        name: String,
    }
    
    struct NFTTransferred has copy, drop {
        nft_id: address,
        from: address,
        to: address,
    }
    
    /// Create a new collection
    public entry fun create_collection(
        name: vector<u8>,
        description: vector<u8>,
        ctx: &mut TxContext
    ) {
        let collection = Collection {
            id: object::new(ctx),
            name: string::utf8(name),
            description: string::utf8(description),
            creator: tx_context::sender(ctx),
            total_supply: 0,
        };
        
        transfer::share_object(collection);
    }
    
    /// Mint a new NFT
    public entry fun mint_nft(
        collection: &mut Collection,
        name: vector<u8>,
        description: vector<u8>,
        url: vector<u8>,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        
        let nft = NFT {
            id: object::new(ctx),
            name: string::utf8(name),
            description: string::utf8(description),
            url: string::utf8(url),
            creator: sender,
        };
        
        collection.total_supply = collection.total_supply + 1;
        
        event::emit(NFTMinted {
            nft_id: object::uid_to_address(&nft.id),
            creator: sender,
            name: string::utf8(name),
        });
        
        transfer::transfer(nft, sender);
    }
    
    /// Transfer an NFT
    public entry fun transfer_nft(
        nft: NFT,
        recipient: address,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        
        event::emit(NFTTransferred {
            nft_id: object::uid_to_address(&nft.id),
            from: sender,
            to: recipient,
        });
        
        transfer::transfer(nft, recipient);
    }
    
    /// Burn an NFT
    public entry fun burn_nft(
        nft: NFT,
        collection: &mut Collection,
    ) {
        let NFT { id, name: _, description: _, url: _, creator: _ } = nft;
        collection.total_supply = collection.total_supply - 1;
        object::delete(id);
    }
    
    /// Get NFT info
    public fun get_nft_info(nft: &NFT): (String, String, String, address) {
        (nft.name, nft.description, nft.url, nft.creator)
    }
}
