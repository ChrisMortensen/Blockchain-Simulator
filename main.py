from ecdsa.keys import SigningKey
import hashlib

class Wallet():

    def __init__(self):
        self.private_key = SigningKey.generate()
        self.public_key = self.private_key.get_verifying_key()
    
    def get_address(self):
        return self.public_key

    def sign(self, data: bytes):
        return self.private_key.sign(data)

    def verify(self, data: bytes, signature: bytes):
        return self.public_key.verify(signature, data)

    def create_transaction(self, recipient_address: bytes, amount: int, utxos: list):
        return Transaction(self, recipient_address, amount, utxos)

    def get_balance(self, utxo_set: list) -> int:
        balance = 0
        for utxo in utxo_set:
            if utxo['owner_address'] == self.get_address():
                balance += utxo['amount']
        return balance



class Transaction():
    
    fee = 1

    def __init__(self, sender_wallet: Wallet, recipient_address: bytes, amount: int, utxos: list):
        self.sender_pubkey = sender_wallet.public_key
        self.recipient_address = recipient_address
        self.inputs = []
        self.outputs = []
        self.amount = amount
        self.utxos = utxos

        # 1. Create inputs (choose UTXOs to cover the amount + fee)
        selected_utxos = []
        total = 0
        i = 0
        while i < len(utxos):
            utxo = utxos[i]
            if utxo['owner_address'] == sender_wallet.get_address():
                selected_utxos.append(utxo)
                total += utxo['amount']
                if total >= self.amount + self.fee:
                    break
            i += 1

        if total < self.amount + self.fee:
            raise ValueError("Insufficient funds")

        self.inputs = selected_utxos

        # 2. Create outputs
        self.outputs.append({'owner_address': recipient_address, 'amount': amount})
        change = total - amount - self.fee
        if change > 0:
            self.outputs.append({'owner_address': sender_wallet.get_address(), 'amount': change})

        # 3. Sign transaction
        self.signature = sender_wallet.sign(self._serialize_for_signing())

        # 4. Compute transaction ID
        self.txid = self._compute_txid()

    def _serialize_for_signing(self):
        """Serialize inputs and outputs deterministically for signing"""
        data = ""
        for input in self.inputs:
            data += f"{input['txid']}:{input['index']};"
        for output in self.outputs:
            data += f"{output['owner_address']}:{output['amount']};"
        return data.encode()

    def _compute_txid(self):
        """Hash serialized content + signature"""
        content = self._serialize_for_signing() + self.signature
        return hashlib.sha256(content).hexdigest()

    def verify(self):
        """Verify signature with sender pubkey"""
        try:
            return self.sender_pubkey.verify(self.signature, self._serialize_for_signing())
        except:
            return False

def print_all_balances(wallets: list, utxo_set: list) -> None:
    for wallet in wallets:
        balance = wallet.get_balance(utxo_set)
        print(f"{wallet.get_address().to_string().hex()}'s balance: {balance}")

if __name__ == "__main__":
    # Create wallets
    alice = Wallet()
    bob = Wallet()
    chris = Wallet()
    wallets = [alice, bob, chris]

    # Initial UTXO set (balances)
    utxo_set = [
        # genesis outputs
        {"txid": "initial_transaction", "index": 0, "amount": 50, "owner_address": alice.get_address()},
        {"txid": "initial_transaction", "index": 1, "amount": 50, "owner_address": bob.get_address()},
        {"txid": "initial_transaction", "index": 2, "amount": 50, "owner_address": chris.get_address()},
    ]

    # Check balances
    print_all_balances(wallets, utxo_set)

    # Alice sends 5 to Bob
    transaction = alice.create_transaction(bob.get_address(), 5, utxo_set)

    # Verify the transaction
    is_valid = transaction.verify()
    print(f"Transaction valid: {is_valid}")

    # Process transaction


    # Check balances
    print_all_balances(wallets, utxo_set)