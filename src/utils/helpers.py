def print_all_balances(wallets: list) -> None:
    for wallet in wallets:
        balance = wallet.get_balance()
        print(f"{wallet.get_address().to_string().hex()}'s balance: {balance}")