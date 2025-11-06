from src.core.transaction import Transaction
from src.core.blockchain import Blockchain
from src.utils.crypto import is_valid_proof

class Node():
    
    def __init__(self, blockchain=None):
        self.blockchain = blockchain or Blockchain()
        self.peers = []
        self.seen_blocks = set()
        self.seen_transactions = set()

    def is_new_transaction(self, txid):
        return not txid in self.seen_transactions

    def receive_transaction(self, transaction):
        if transaction.txid in self.seen_transactions:
            return False
        self.seen_transactions.add(transaction.txid)

        if not transaction.verify():
            return False
        
        self.blockchain.mempool.append(transaction)

        self._propegate_transaction(transaction)
        
        return True

    def _propegate_transaction(self, transaction):
        for peer in self.peers:
            if peer.is_new_transaction(transaction.txid):
                peer.receive_transaction(transaction)
        return

    def receive_block(self, block):
        if block.hash in self.seen_blocks:
            return False
        self.seen_blocks.add(block.hash)
        
        if not self._is_block_valid(block):
            return False
        
        self._propegate_block(block)

        self.blockchain.append_block(block)
        
        return True
    
    def _propegate_block(self, block):
        for peer in self.peers:
            peer.receive_block(block)
        return
    
    def _is_block_valid(self, block):
        for tx in block.transactions[1:]:
            if tx not in self.blockchain.mempool:
                raise ValueError("Invalid transactions")
        
        prev_hash = self.blockchain.last_block_hash
        if block.prev_hash != prev_hash:
            raise ValueError("Invalid previous hash")

        block.compute_hash()
        is_valid_hash = is_valid_proof(block.hash, self.blockchain.difficulty)
        if not is_valid_hash:
            raise ValueError("Invalid proof of work")
        
        reward_tx = block.transactions[0]
        reward_amount = self.blockchain.block_subsidy + Transaction.fee * (len(block.transactions) - 1)
        if reward_tx.amount != reward_amount:
            raise ValueError("Invalid reward amount")
        return True