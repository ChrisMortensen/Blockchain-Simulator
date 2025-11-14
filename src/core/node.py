from src.core.transaction import Transaction
from src.core.blockchain import Blockchain
from src.utils.crypto import is_valid_proof

class Node():
    
    def __init__(self, blockchain=None):
        self.blockchain = blockchain or Blockchain()
        self.peers = set()
        self.seen_blocks = set()
        self.seen_transactions = set()
        self.orphan_blocks = {}

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

    def receive_block(self, block):
        if block.hash in self.seen_blocks:
            return False
        self.seen_blocks.add(block.hash)
        
        if not self._is_block_valid(block):
            return False
        
        sucess = self._try_add_block(block)

        if sucess:
            self._propegate_block(block)
        
        return sucess
    
    def _try_add_block(self, block):
        if block.prev_hash == self.blockchain.last_block_hash:
            return self.blockchain.append_block(block)
        
        previous_block = self._find_block_by_hash(block.prev_hash)
        if previous_block:
            return self._handle_fork(block)
        
        self.orphan_blocks[block.hash] = block
        return False

    def _handle_fork(self, block):
        alternative_chain = self._build_alternative_chain(block)
        if not alternative_chain:
            return False
        
        current_chain_length = len(self.blockchain.chain)
        alternative_chain_length = len(alternative_chain)
                
        if alternative_chain_length > current_chain_length:
            return self._switch_to_chain(alternative_chain)
        
        return False
    
    def _switch_to_chain(self, new_chain):
        if not self._validate_chain(new_chain):
            return False
        
        old_chain = self.blockchain.chain.copy()
        old_utxo_set = self.blockchain.utxo_set.copy()

        self.blockchain.chain = []
        self.blockchain.utxo_set = []
        
        for block in new_chain:
            if not self.blockchain.append_block(block):
                # Use old chain if appending fails
                self.blockchain.chain = old_chain
                self.blockchain.utxo_set = old_utxo_set
                return False
        
        self._remove_used_orphans()
        return True

    def _validate_chain(self, chain):   
        for i in range(1, len(chain)):
            if chain[i].prev_hash != chain[i-1].hash:
                # Invalid block pair
                return False
        
            if not self._is_block_valid(chain[i]):
                # Invalid block
                return False
            
        return True

    def _remove_used_orphans(self):
        chain_hashes = {block.hash for block in self.blockchain.chain}
        orphan_blocks = {}
        for hash, block in self.orphan_blocks.items():
            if hash not in chain_hashes:
                orphan_blocks[hash] = block
        self.orphan_blocks = orphan_blocks

    def _build_alternative_chain(self, tip_block):
        chain = [tip_block]
        current_block = tip_block
        
        # Walk backwards from tip to genesis
        while current_block.prev_hash != self.blockchain.chain[0].hash:
            parent = self._find_block_by_hash(current_block.prev_hash)
            if not parent:
                return None
            chain.insert(0, parent)
            current_block = parent
        
        chain.insert(0, self.blockchain.chain[0])
        return chain

    def _find_block_by_hash(self, block_hash):
        for block in self.blockchain.chain:
            if block.hash == block_hash:
                return block
        
        return self.orphan_blocks.get(block_hash)

    def _propegate_block(self, block):
        for peer in self.peers:
            peer.receive_block(block)
        return
    
    def _is_block_valid(self, block):
        block.compute_hash()
        is_valid_hash = is_valid_proof(block.hash, block.difficulty)
        if not is_valid_hash:
            # Invalid proof of work
            return False
        
        reward_tx = block.transactions[0]
        reward_amount = self.blockchain.block_subsidy + Transaction.fee * (len(block.transactions) - 1)
        if reward_tx.amount != reward_amount:
            # Invalid reward amount
            return False
        
        return True