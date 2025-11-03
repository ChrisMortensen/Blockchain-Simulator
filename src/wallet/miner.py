import time

from src.core.transaction import Transaction
from src.core.block import Block
from src.wallet.wallet import Wallet
from src.utils.crypto import is_valid_proof

MINER_POW_SLEEP = 0.025 # Limit computation requirements

class Miner(Wallet):
    
    def __init__(self):
        super().__init__()

    def mine(self, blockchain):
        # Needs to make a new thread
        while True:
            prev_hash = blockchain.last_block_hash
            transactions = blockchain.mempool.copy()
            reward_amount = blockchain.block_subsidy + Transaction.fee * len(transactions)
            reward_tx = Transaction.coinbase(
                recipient_address=self.get_address(),
                reward=reward_amount
            )
            transactions.insert(0, reward_tx)

            block = Block(transactions, prev_hash)
            self._solve_block(block, blockchain)
            return # No thred so for now just run once
    
    def _solve_block(self, block, blockchain):
        prev_hash = blockchain.last_block_hash
        while block.prev_hash == prev_hash:
            block.compute_hash()
            is_valid = is_valid_proof(blockchain, block)
            if is_valid:
                blockchain.validator.validate(block) # Implement handeling of wrong return 
                # Maby a sleep is needed here, so the validator has time to process and miner doesnt start solving the same block
                return
            else:
                time.sleep(MINER_POW_SLEEP)
                block.nonce += 1 # Change this so different miners dont interate over the same values
                prev_hash = blockchain.last_block_hash