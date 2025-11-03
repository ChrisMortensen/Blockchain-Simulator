class Block():

    def __init__(self, transactions, prev_hash):
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.hash = None
        self.nonce = 0

    def compute_hash(self):
        data = self.prev_hash + str(self.transactions) + str(self.nonce)
        import hashlib
        self.hash = hashlib.sha256(data.encode()).hexdigest()