def is_valid_proof(hash: str, difficulty: int):
    hash_int = int(hash, 16)
    target = (1 << (256 - difficulty)) - 1
    return hash_int <= target