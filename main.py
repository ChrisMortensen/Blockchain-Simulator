from ecdsa.keys import SigningKey
import hashlib
import time

MINER_POW_SLEEP = 0.025 # Limit computation requirements

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
        return Transaction(sender_wallet=self, recipient_address=recipient_address, amount=amount, utxos=utxos)

    def get_balance(self, utxo_set: list) -> int:
        balance = 0
        for utxo in utxo_set:
            if utxo['owner_address'] == self.get_address():
                balance += utxo['amount']
        return balance


class Transaction():
    
    fee = 1

    def __init__(self, recipient_address: bytes, amount: int, utxos: list, sender_wallet: Wallet = None, is_coinbase: bool = False):
        self.recipient_address = recipient_address
        self.inputs = []
        self.outputs = []
        self.amount = amount
        self.utxos = utxos

        if is_coinbase:
            self.sender_public_key = None
            self.sender_address = None
            self.outputs.append({'owner_address': recipient_address, 'amount': amount})
            self.signature = b''
            self.txid = self._compute_txid()
            return
        
        if sender_wallet is None:
            raise ValueError("sender_wallet is required for non-coinbase transactions")
        
        self.sender_public_key = sender_wallet.public_key
        self.sender_address = sender_wallet.get_address()

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
        if self.sender_public_key is None: # Miner reward transaction
            return True
        try:
            return self.sender_public_key.verify(self.signature, self._serialize_for_signing())
        except:
            return False


class Blockchain():

    def __init__(self):
        self.chain = []
        self.utxo_set = []
        self.mempool = []
        self.difficulty = 3
        self.block_subsidy = 2
        self.validator = Validator(self)

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


class Block():

    def __init__(self, transactions, prev_hash):
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.hash = None
        self.nonce = 0

    def compute_hash(self):
        data = self.prev_hash + str(self.transactions) + str(self.nonce)
        self.hash = hashlib.sha256(data.encode()).hexdigest()


class Miner(Wallet):
    
    def __init__(self):
        super().__init__()

    def mine(self, blockchain):
        # Needs to make a new thread
        while True:
            prev_hash = blockchain.last_block_hash
            transactions = blockchain.mempool.copy()
            reward_amount = blockchain.block_subsidy + Transaction.fee * len(transactions)
            reward_tx = Transaction(
                sender_wallet=None,
                recipient_address=miner.get_address(),
                amount=reward_amount,
                utxos=[],
                is_coinbase=True
            )
            transactions.insert(0,reward_tx)

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


class Validator():
    
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def validate(self, block):
        for tx in block.transactions[1:]:
            if tx not in self.blockchain.mempool:
                raise ValueError("Invalid transactions")
        
        prev_hash = self.blockchain.last_block_hash
        if block.prev_hash is not prev_hash:
            raise ValueError("Invalid previous hash")

        block.compute_hash()
        is_valid_hash = is_valid_proof(self.blockchain, block)
        if not is_valid_hash:
            raise ValueError("Invalid proof of work")
        
        reward_tx = block.transactions[0]
        reward_amount = blockchain.block_subsidy + Transaction.fee * (len(block.transactions) - 1)
        if reward_tx.amount is not reward_amount:
            raise ValueError("Invalid reward amount")

        self.blockchain.append_block(block)
        
        return True


def is_valid_proof(blockchain, block):
    hash_int = int(block.hash, 16)
    target = (1 << (256 - blockchain.difficulty)) - 1
    return hash_int <= target

def print_all_balances(wallets: list, utxo_set: list) -> None:
    for wallet in wallets:
        balance = wallet.get_balance(utxo_set)
        print(f"{wallet.get_address().to_string().hex()}'s balance: {balance}")

if __name__ == "__main__":
    # Initialize environment
    blockchain = Blockchain()
    alice = Wallet()
    bob = Wallet()
    chris = Wallet()
    miner = Miner()
    wallets = [alice, bob, chris, miner]
    genesis_utxo_set = [
        {"txid": "initial_transaction", "index": 0, "amount": 50, "owner_address": alice.get_address()},
        {"txid": "initial_transaction", "index": 1, "amount": 50, "owner_address": bob.get_address()},
        {"txid": "initial_transaction", "index": 2, "amount": 50, "owner_address": chris.get_address()},
    ]
    blockchain.add_genesis_utxos(genesis_utxo_set)

    # Check initial balances
    print("\nInitial Balances")
    print_all_balances(wallets, blockchain.utxo_set)

    # Alice sends 5 to Bob
    tx1 = alice.create_transaction(bob.get_address(), 5, blockchain.utxo_set)
    # Chris sends 7 to Bob
    tx2 = chris.create_transaction(bob.get_address(), 7, blockchain.utxo_set)
    # Append transactions to blockchain
    blockchain.mempool.extend([tx1, tx2])

    # Process transactions
    miner.mine(blockchain)

    # Check final balances
    print("\nFinal Balances")
    print_all_balances(wallets, blockchain.utxo_set)