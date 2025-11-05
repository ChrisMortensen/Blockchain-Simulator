from src.core.node import Node

class Network():
    def __init__(self, node_amount):
        self.nodes = self._create_nodes(node_amount)
        self.peer_connections = 3

        self._connect_nodes()

    def _create_nodes(self, node_amount):
        nodes = []
        for i in range(0,node_amount):
            node = Node()
            nodes.append(node)

        return nodes
    
    def _connect_nodes(self):
        for node_id, node in enumerate(self.nodes):
            for peer_num in range(1, self.peer_connections+1):
                peer_id = (node_id + peer_num) % len(self.nodes)
                node.peers.append(self.nodes[peer_id])

    def add_genesis_utxos(self, initial_utxos):
        for node in self.nodes:
            node.blockchain.utxo_set.extend(initial_utxos)