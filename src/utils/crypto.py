def is_valid_proof(blockchain, block):
    hash_int = int(block.hash, 16)
    target = (1 << (256 - blockchain.difficulty)) - 1
    return hash_int <= target