import time
import random
import threading

from src.core.transaction import Transaction
from src.core.block import Block
from src.wallet.wallet import Wallet
from src.utils.crypto import is_valid_proof

MINER_POW_SLEEP = 0.025 # Limit computation requirements

class Miner(Wallet):
    
    def __init__(self):
        super().__init__()
        self.is_mining = False
        self.mining_thread = None

    def start_mining(self):
        if not self.is_mining:
            self.is_mining = True
            self.miner_thread = threading.Thread(target=self._mine)
            self.miner_thread.daemon = True
            self.miner_thread.start()

    def stop_mining(self):
        if self.is_mining:
            self.miner_thread.join()
            self.is_mining = False

    def _mine(self):
        if not self.peers:
            raise ValueError("Miner must be attached to a node")
        
        self.primary_node = random.choice(list(self.peers))
        blockchain = self.primary_node.blockchain

        while True:
            prev_hash = blockchain.last_block_hash
            transactions = blockchain.mempool.copy()
            reward_amount = blockchain.block_subsidy + Transaction.fee * len(transactions)
            
            reward_tx = Transaction.coinbase(
                recipient_address=self.get_address(),
                reward=reward_amount
            )
            transactions.insert(0, reward_tx)

            block = Block(transactions, prev_hash, blockchain.difficulty)
            self._solve_block(block)
    
    def _solve_block(self, block):
        while True:
            block.compute_hash()

            if is_valid_proof(block.hash, self.primary_node.blockchain.difficulty):
                self.primary_node.receive_block(block)
                return

            if block.prev_hash != self.primary_node.blockchain.last_block_hash:
                return

            time.sleep(MINER_POW_SLEEP)
            block.nonce += 1 # Change this so different miners dont interate over the same values