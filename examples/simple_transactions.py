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
    genesis_utxo_set = []
    initial_balance = 50
    for ID, wallet in enumerate(network.wallets):
        genesis_utxo_set.append({"txid": "initial_transaction", "index": ID, "amount": initial_balance, "owner_address": wallet.get_address()})
    network.add_genesis_utxos(genesis_utxo_set)

    # Check initial balances
    print("\nInitial Balances")
    print_all_balances(wallets)

    # Alice sends 5 to Bob
    alice.create_transaction(bob.get_address(), 5)
    # Chris sends 10 to Bob
    chris.create_transaction(bob.get_address(), 10)

    # Process transactions
    miner.start_mining()

    # Wait for new block
    while blockchain.get_best_block().height < 1:
        time.sleep(0.001)

    # Check final balances
    print("\nFinal Balances")
    print_all_balances(wallets)