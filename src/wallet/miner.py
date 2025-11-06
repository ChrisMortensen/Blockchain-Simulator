import time

from src.core.transaction import Transaction
from src.core.block import Block
from src.wallet.wallet import Wallet
from src.utils.crypto import is_valid_proof

MINER_POW_SLEEP = 0.025 # Limit computation requirements

class Miner(Wallet):
    
    def __init__(self, node=None):
        super().__init__()
        self.node = node

    def mine(self):
        # Needs to make a new thread
        if not self.node:
            raise ValueError("Miner must be attached to a node")
        
        blockchain = self.node.blockchain

        while True:
            prev_hash = blockchain.last_block_hash
            transactions = blockchain.mempool.copy()
            reward_amount = blockchain.block_subsidy + Transaction.fee * len(transactions)
            
            reward_tx = Transaction.coinbase(
                recipient_address=self.get_address(),
                reward=reward_amount
            )
            transactions.insert(0, reward_tx)

            block = Block(transactions, prev_hash, self.node.blockchain.difficulty)
            self._solve_block(block)
            return # No thred so for now just run once
    
    def _solve_block(self, block):
        while True:
            block.compute_hash()

            if is_valid_proof(block.hash, self.node.blockchain.difficulty):
                self.node.receive_block(block)
                return

            if block.prev_hash != self.node.blockchain.last_block_hash:
                return

            time.sleep(MINER_POW_SLEEP)
            block.nonce += 1 # Change this so different miners dont interate over the same values