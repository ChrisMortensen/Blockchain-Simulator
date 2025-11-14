import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import Network
from src.utils import print_all_balances

if __name__ == "__main__":
    # Initialize environment
    network = Network(node_amount=1,wallet_amount=3,miner_amount=1)
    alice, bob, chris = network.wallets[0:3]
    node = network.nodes[0]
    blockchain = node.blockchain
    miner = network.miners[0]
    wallets = network.wallets + network.miners
    genesis_utxo_set = [
        {"txid": "initial_transaction", "index": 0, "amount": 50, "owner_address": alice.get_address()},
        {"txid": "initial_transaction", "index": 1, "amount": 50, "owner_address": bob.get_address()},
        {"txid": "initial_transaction", "index": 2, "amount": 50, "owner_address": chris.get_address()},
    ]
    network.add_genesis_utxos(genesis_utxo_set)

    # Check initial balances
    print("\nInitial Balances")
    print_all_balances(wallets)

    # Alice sends 5 to Bob
    alice.create_transaction(bob.get_address(), 5)
    # Chris sends 10 to Bob
    chris.create_transaction(bob.get_address(), 10)

    # Get last block hash so we know when the transactions have been processed
    latest_block = blockchain.last_block_hash

    # Process transactions
    miner.start_mining()

    while latest_block == blockchain.last_block_hash:
        time.sleep(0.001)

    # Check final balances
    print("\nFinal Balances")
    print_all_balances(wallets)