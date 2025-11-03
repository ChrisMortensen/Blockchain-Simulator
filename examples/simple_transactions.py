import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import Blockchain
from src.wallet import Wallet, Miner
from src.utils import print_all_balances

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