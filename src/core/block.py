import time

class Block():

    def __init__(self, transactions, prev_hash, difficulty, height=0):
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.difficulty = difficulty
        self.height = height
        self.timestamp = time.time()
        self.nonce = 0

    @property
    def hash(self):
        hash = self.compute_hash()
        return hash

    def compute_hash(self):
        # Add timestamp and height, maybe merkle root later
        data = self.prev_hash + str(self.transactions) + str(self.nonce) + str(self.difficulty)
        import hashlib
        hash = hashlib.sha256(data.encode()).hexdigest()
        return hash