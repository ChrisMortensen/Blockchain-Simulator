import streamlit as st
from pyvis.network import Network as pyvis_Network
import streamlit.components.v1 as components
import random

from src.core.network import Network
from src.core.node import Node
from src.wallet.wallet import Wallet
from src.wallet.miner import Miner

st.set_page_config(
    page_title="Blockchain Visualizer",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
/* Network stats containers */
.metric-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 12px;
    border-radius: 10px;
    margin: 8px 0;
    color: black;
}

.metric-nodes { background-color: #e8f5e8; }
.metric-edges { background-color: #e3f2fd; }
.metric-distribution { background-color: #f3e5f5; }

            
.metric-label {
    text-align: center;
    font-size: 1rem;
    margin-bottom: 4px;
    font-weight: bold;
}
            
.metric-value {
    text-align: center;
    font-size: 1.4rem;
    margin: 0;
}

.node-type-label{
    text-align: center;
    font-weight: bold;
}
                   
.center-text { text-align: center; }
</style>
""", unsafe_allow_html=True)

class NetworkVisualizer:

    node_types = ["miner","wallet","node"]
    node_properties = {
        "miner": {"color": "#FF6B35", "size": 30, "shape": "diamond"},
        "wallet": {"color": "#00A896", "size": 30, "shape": "dot"}, 
        "node": {"color": "#004E89", "size": 30, "shape": "dot"}
    }

    def __init__(self, blockchain_network, show_labels=True):
        self.network = blockchain_network
        self.show_labels = show_labels
        self.pyvis_net = pyvis_Network(height="700px", width="100%", bgcolor="#222222", font_color="white")
        self.wallet_names = {}

    def _give_wallets_names(self):
        from faker import Faker
        faker = Faker('en_US')
        wallets = self.network.wallets
        for wallet in wallets:
            public_key = wallet.get_address().to_string().hex()
            random_name = faker.name()
            self.wallet_names[public_key] = random_name

    @property
    def all_nodes(self):
        return self.network.nodes + self.network.wallets + self.network.miners
    
    def _get_node_index(self, node):
        for i, other in enumerate(self.network.nodes):
            if node == other:
                return i

    def _get_node_type(self, node):
        node_type_map = {
            Node: "node",
            Wallet: "wallet", 
            Miner: "miner"
        }
        return node_type_map.get(type(node), "unknown")

    def _add_nodes_to_graph(self):
        start_id = len(self.pyvis_net.nodes)

        for i, node in enumerate(self.all_nodes):
            node_id = start_id + i
            node_type = self._get_node_type(node)
            properties = NetworkVisualizer.node_properties[node_type]
            if node_type == 'wallet':
                node_public_key = node.get_address().to_string().hex()
                node_name = self.wallet_names[node_public_key]
                label = node_name
            else:
                label = f"{node_type} {i}"
            if not show_labels: label = ""

            if isinstance(node, Wallet):
                random_peer = random.choice(list(node.peers))
                balance = node.get_balance(random_peer.blockchain.utxo_set)
                title = f"Balance: {balance}"
            if isinstance(node, Node):
                peer_total = len(node.peers)
                title = f"Peers: {peer_total}"
            
            self.pyvis_net.add_node(
                node_id, 
                label=label,
                color=properties["color"],
                size=properties["size"], 
                shape=properties["shape"],
                title=title # On hover
            )

    def _add_edges_to_graph(self):
        for node_id, node in enumerate(self.all_nodes):
            if hasattr(node, 'peers'):
                for peer in node.peers:
                    peer_index = self._get_node_index(peer)
                    if peer_index != None:
                        self.pyvis_net.add_edge(node_id, peer_index, width=1.5)

    def generate_visualization(self):
        self._give_wallets_names()
        self._add_nodes_to_graph()
        self._add_edges_to_graph()
        self.pyvis_net.set_options("""
        var options = {
            "physics": {
                "enabled": true,
                "stabilization": {"iterations": 200},
                "repulsion": {
                "nodeDistance": 200,
                "centralGravity": 0.1,
                "springLength": 200,
                "springConstant": 0.01,
                "damping": 0.12
                },
                "solver": "repulsion"
            }
        }
        """)

    def get_html_content(self):
        self.pyvis_net.save_graph("blockchain_network.html")
        with open("blockchain_network.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Remove all borders surrounding the network (Yes they are all needed)
        html_content = html_content.replace(
            '<div class="card" style="width: 100%">',
            '<div class="card" style="width: 100%; border: none;">'
        )
        
        html_content = html_content.replace(
            '<div id="mynetwork" class="card-body">',
            '<div id="mynetwork" class="card-body" style="border: none; padding: 0;">'
        )
        
        border_removal_css = """
        <style>
            h1, center{
                display: none;
            }
        </style>
        """
        
        html_content = html_content.replace('</head>', border_removal_css + '</head>')
        
        return html_content

def generate_network():
    network = Network(node_amount, wallet_amount, miner_amount, min_node_peers, min_wallet_peers, min_miner_peers)

    visualizer = NetworkVisualizer(network, show_labels)
    visualizer.generate_visualization()
    html_content = visualizer.get_html_content()

    st.session_state.html_content = html_content
    st.session_state.network_generated = True
    st.session_state.actual_network = network
    st.session_state.pyvis_net = visualizer.pyvis_net

with st.sidebar:
    st.title("Blockchain Network Visualizer")
    st.write("Visualize blockchain networks of varying complexity")
    st.write("`Created by:`")
    linkedin_url = "https://www.linkedin.com/in/christiansvalgaard/"
    st.markdown(f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Christian S. Mortensen`</a>', unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Network Size")
    wallet_amount = st.slider("Wallets", 0, 20, 10)
    miner_amount = st.slider("Miners", 0, 50, 25)
    node_amount = st.slider("Nodes", 10, 90, 50)
    
    st.markdown("---")

    st.subheader("Peer Connections")
    min_wallet_peers = st.slider("Wallet Min Peers", 1, 6, 2)
    min_miner_peers = st.slider("Miner Min Peers", 1, 6, 2)
    min_node_peers = st.slider("Node Min Peers", 1, 8, 4)

    st.markdown("---")

    st.subheader("Network Options")
    show_labels = st.checkbox("Show Node Labels", value=True)
    
    st.markdown("---")

    generate_btn = st.button("Generate Network", type="primary")

if 'network_generated' not in st.session_state:
    st.session_state.network_generated = False

if generate_btn or not st.session_state.network_generated:
    generate_network()

def display_node_types():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="node-type-label" style="color: #00A896;">🟢 Wallets</div>
            <div class="center-text">User accounts: Signs off on transactions</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="node-type-label" style="color: #004E89;">🔵 Nodes</div>
            <div class="center-text">Network: Stores, relays, and validates blockchain data</div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="node-type-label" style="color: #FF6B35;">🔶 Miners</div>
            <div class="center-text">Block creators: Processes transactions for rewards</div>
        """, unsafe_allow_html=True)

def display_network_structure():
    col1, col2, col3 = st.columns(3)
    pyvis_net = st.session_state.pyvis_net
    with col1:
        node_amount_stat = len(pyvis_net.nodes)
        st.markdown(f"""
            <div class="metric-container metric-nodes">
                <div>
                    <div class="metric-label">Total Nodes</div>
                    <div class="metric-value">{node_amount_stat}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        edge_amount_stat = len(pyvis_net.edges)
        st.markdown(f"""
            <div class="metric-container metric-edges">
                <div>
                    <div class="metric-label">Total Connections</div>
                    <div class="metric-value">{edge_amount_stat}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        network = st.session_state.actual_network
        miners = len(network.miners)
        wallets = len(network.wallets)
        nodes = len(network.nodes)
        
        st.markdown(f"""
            <div class="metric-container metric-distribution">
                <div>
                    <div class="metric-label">Network Structure</div>
                    <div class="metric-value">Miners: {miners}   Wallets: {wallets}   Nodes: {nodes}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def display_main_page():
    st.title("Crypto Network Visualizer")
    st.write("Interactive visualization of cryptocurrency network nodes and connections")
    st.markdown("---")  

    display_node_types()
    st.markdown("---")  
    
    # Display network  
    components.html(st.session_state.html_content, height=700)
    #st.markdown("---")

    # Display tip
    #st.info("Drag nodes to rearrange the network. Zoom with mouse wheel.")

    display_network_structure()
    #st.markdown("---")

display_main_page()