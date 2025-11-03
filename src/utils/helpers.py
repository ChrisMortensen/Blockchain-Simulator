def print_all_balances(wallets: list, utxo_set: list) -> None:
    for wallet in wallets:
        balance = wallet.get_balance(utxo_set)
        print(f"{wallet.get_address().to_string().hex()}'s balance: {balance}")