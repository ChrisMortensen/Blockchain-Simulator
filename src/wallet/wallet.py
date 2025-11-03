from src.core.transaction import Transaction

class Wallet():

    def __init__(self):
        from ecdsa.keys import SigningKey
        self.private_key = SigningKey.generate()
        self.public_key = self.private_key.get_verifying_key()
    
    def get_address(self):
        return self.public_key

    def sign(self, data: bytes):
        return self.private_key.sign(data)

    def verify(self, data: bytes, signature: bytes):
        return self.public_key.verify(signature, data)

    def get_balance(self, utxo_set: list) -> int:
        balance = 0
        for utxo in utxo_set:
            if utxo['owner_address'] == self.get_address():
                balance += utxo['amount']
        return balance

    def create_transaction(self, recipient_address: bytes, amount: int, utxos: list):
        # Create inputs (choose UTXOs to cover the amount + fee)
        inputs = []
        total = 0
        charge = amount + Transaction.fee
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

        return tx