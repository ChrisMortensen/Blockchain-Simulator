from src.core.transaction import Transaction
from src.utils.crypto import is_valid_proof

class Validator():
    
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def validate(self, block):
        for tx in block.transactions[1:]:
            if tx not in self.blockchain.mempool:
                raise ValueError("Invalid transactions")
        
        prev_hash = self.blockchain.last_block_hash
        if block.prev_hash is not prev_hash:
            raise ValueError("Invalid previous hash")

        block.compute_hash()
        is_valid_hash = is_valid_proof(self.blockchain, block)
        if not is_valid_hash:
            raise ValueError("Invalid proof of work")
        
        reward_tx = block.transactions[0]
        reward_amount = self.blockchain.block_subsidy + Transaction.fee * (len(block.transactions) - 1)
        if reward_tx.amount is not reward_amount:
            raise ValueError("Invalid reward amount")

        self.blockchain.append_block(block)
        
        return True