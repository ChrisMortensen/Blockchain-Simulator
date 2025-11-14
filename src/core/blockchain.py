from src.core.transaction import Transaction
from src.core.block import Block

class Blockchain():

    def __init__(self):
        self.chain = []
        self.utxo_set = []
        self.mempool = []
        self.difficulty = 5
        self.block_subsidy = 2
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = Block(transactions=[], prev_hash="0" * 64, difficulty=self.difficulty, height=0)
        genesis.compute_hash()
        self.chain.append(genesis)

    def get_best_block(self):
        if not self.chain:
            return None
        best = self.chain[-1]
        return best

    def add_transaction(self, transaction: Transaction):
        self.mempool.append(transaction)

    @property
    def last_block_hash(self):
        if not self.chain:
            return '0' * 64
        return self.chain[-1].hash
    
    def append_block(self, block):
        regular_tx_list = block.transactions[1:]
        for tx in regular_tx_list:
            if tx not in self.mempool:
                # Invalid transaction
                return False

            if not tx.verify():
                # Invalid signature
                return False

            for input in tx.inputs:
                if input not in self.utxo_set or input['owner_address'] != tx.sender_address:
                    # Invalid utxo
                    return False

        self.chain.append(block)

        for tx in list(block.transactions):
            if tx != block.transactions[0]:
                for input in tx.inputs:
                    self.utxo_set.remove(input)
            
            for index, output in enumerate(tx.outputs):
                new_utxo = {
                    "txid": tx.txid,
                    "index": index,
                    "amount": output['amount'],
                    "owner_address": output['owner_address']
                }
                self.utxo_set.append(new_utxo)
            
            if tx in self.mempool:
                self.mempool.remove(tx)
        return True