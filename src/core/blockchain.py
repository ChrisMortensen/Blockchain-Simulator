from src.core.transaction import Transaction

class Blockchain():

    def __init__(self):
        self.chain = []
        self.utxo_set = []
        self.mempool = []
        self.difficulty = 3
        self.block_subsidy = 2

    def add_genesis_utxos(self, initial_utxos):
        self.utxo_set.extend(initial_utxos)
    
    def add_transaction(self, transaction: Transaction):
        self.mempool.append(transaction)

    @property
    def last_block_hash(self):
        if not self.chain:
            return '0' * 64
        return self.chain[-1].hash 
    
    def append_block(self, block):
        self.chain.append(block)

        for tx in list(block.transactions):
            if not tx.verify():
                raise ValueError("Invalid signature")

            for input in tx.inputs:
                if input not in self.utxo_set or input['owner_address'] != tx.sender_address:
                    raise ValueError("Invalid UTXO")

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