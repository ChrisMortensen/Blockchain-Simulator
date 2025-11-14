from src.core.transaction import Transaction

class Wallet():

    def __init__(self):
        from ecdsa.keys import SigningKey
        self.private_key = SigningKey.generate()
        self.public_key = self.private_key.get_verifying_key()
        self.peers = set()
    
    def get_address(self):
        return self.public_key

    def sign(self, data: bytes):
        return self.private_key.sign(data)

    def verify(self, data: bytes, signature: bytes):
        return self.public_key.verify(signature, data)

    def get_balance(self) -> int:
        balances = []
        for node in self.peers:
            try:
                utxo_set = node.blockchain.utxo_set
                balance = 0
                for utxo in utxo_set:
                    if utxo['owner_address'] == self.get_address():
                        balance += utxo['amount']
                balances.append(balance)
            except:
                continue
        
        if not balances:
            return 0
        
        balances.sort()
        return balances[len(balances) // 2]

    def create_transaction(self, recipient_address, amount):
        # Create inputs (choose UTXOs to cover the amount + fee)
        inputs = []
        total = 0
        charge = amount + Transaction.fee

        from random import choice
        peer_node = choice(list(self.peers))
        utxos = peer_node.blockchain.utxo_set

        for utxo in utxos:
            if utxo['owner_address'] == self.get_address():
                inputs.append(utxo)
                total += utxo['amount']
                if total >= charge:
                    break
        if total < charge:
            raise ValueError("Insufficient funds")

        # Create outputs
        outputs = [{'owner_address': recipient_address, 'amount': amount}]
        change = total - charge
        if change > 0:
            outputs.append({'owner_address': self.get_address(), 'amount': change})

        # Sign transaction
        tx = Transaction(self.get_address(), recipient_address, amount, inputs, outputs)
        signature = self.sign(tx._serialize_for_signing())
        tx.signature = signature

        self._propegate_transaction(tx)
    
    def _propegate_transaction(self, transaction):
        for peer in self.peers:
            if peer.is_new_transaction(transaction.txid): # Check to avoid sending unnecessary data
                peer.receive_transaction(transaction)
        return