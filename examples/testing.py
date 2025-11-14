import sys
import os
import time
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import Network

if __name__ == "__main__":
    # Initialize environment
    network = Network(node_amount=20,miner_amount=20,wallet_amount=20,min_node_peers=4,min_miner_peers=4,min_wallet_peers=4)
    genesis_utxo_set = []
    initial_balance = 100
    for ID, wallet in enumerate(network.wallets):
        genesis_utxo_set.append({"txid": "initial_transaction", "index": ID, "amount": initial_balance, "owner_address": wallet.get_address()})
    network.add_genesis_utxos(genesis_utxo_set)

    for miner in network.miners:
        miner.start_mining()

    timestamp = time.time()
    while True:
        if time.time() - timestamp >= 3:
            timestamp = time.time()
            sender = random.choice(network.wallets)
            receiver = random.choice(network.wallets)
            print("---")
            print(f"Sender: {sender.get_balance()}")
            print(f"Receiver: {receiver.get_balance()}")
            amount = random.randint(1,3)
            sender.create_transaction(receiver.get_address(), amount)
            time.sleep(1)
            print(f"Sender: {sender.get_balance()}")
            print(f"Receiver: {receiver.get_balance()}")
