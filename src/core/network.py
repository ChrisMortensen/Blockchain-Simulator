from src.core.node import Node
from src.wallet.wallet import Wallet
from src.wallet.miner import Miner

import random

class Network():
    def __init__(self, node_amount=10, wallet_amount=2, miner_amount=5,
                 min_node_peers=8, min_wallet_peers=4, min_miner_peers=4):
        self.nodes = self._create_nodes(node_amount, "Node")
        self.wallets = self._create_nodes(wallet_amount, "Wallet")  
        self.miners = self._create_nodes(miner_amount, "Miner")

        self.min_node_peers = min_node_peers
        self.min_wallet_peers = min_wallet_peers
        self.min_miner_peers = min_miner_peers
        
        self._connect_all_nodes()

    def _connect_all_nodes(self):
        self._connect_node_group(self.nodes, self.min_node_peers)
        self._connect_node_group(self.miners, self.min_miner_peers)
        self._connect_node_group(self.wallets, self.min_wallet_peers)

    def _connect_node_group(self, nodes, connections):
        if nodes == self.nodes:
            self._generate_network()
            return
        for node in nodes:
            self._connect_to_network(node, connections)

    def _connect_to_network(self, node, connections):
        node_amount = len(self.nodes)
        start_idx = random.randrange(node_amount)

        for i in range(connections):
            peer_idx = (start_idx + i) % node_amount
            node.peers.add(self.nodes[peer_idx])

    def _create_nodes(self, node_amount, node_type="Node"):
        nodes = []
        for i in range(0, node_amount):
            if node_type == "Miner":
                node = Miner()
            elif node_type == "Wallet":
                node = Wallet()
            else:
                node = Node()
            nodes.append(node)
        return nodes
    
    def _generate_network(self):
        for node in self.nodes:
            possible_peers = [n for n in self.nodes if n != node]
            new_peers = random.sample(
                possible_peers, 
                k=min(self.min_node_peers, len(possible_peers))
            )
            for peer in new_peers:
                node.peers.add(peer)
                peer.peers.add(node)

    def add_genesis_utxos(self, initial_utxos):
        for node in self.nodes:
            node.blockchain.utxo_set.extend(initial_utxos)