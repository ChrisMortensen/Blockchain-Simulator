class Transaction():
    
    fee = 1

    def __init__(self, sender_address, recipient_address, amount, inputs, outputs, signature=b"", txid=None):
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.amount = amount
        self.inputs = inputs
        self.outputs = outputs
        self.signature = signature
        self.txid = txid or self._compute_txid()

    def _serialize_for_signing(self): # Ideally convert it to bytes or hex
        """Serialize inputs and outputs deterministically for signing"""
        data = []

        sender_hex = self.sender_address.to_string().hex() if self.sender_address else ""
        data.append(sender_hex)

        for input in sorted(self.inputs, key=lambda x: (x['txid'], x['index'])):
            data.append(f"{input['txid']}:{input['index']}")

        for output in sorted(self.outputs, key=lambda x: x['owner_address'].to_string().hex()):
            data.append(f"{output['owner_address'].to_string().hex()}:{output['amount']}")

        data = ";".join(data)
        return data.encode()

    def _compute_txid(self):
        """Hash serialized content"""
        import hashlib
        content = self._serialize_for_signing()
        return hashlib.sha256(content).hexdigest()

    def verify(self):
        """Verify signature with sender pubkey"""
        if self.sender_address is None: # Miner reward transaction
            return True
        try:
            return self.sender_address.verify(self.signature, self._serialize_for_signing())
        except:
            return False
        
    @classmethod
    def coinbase(self, recipient_address, reward):
        outputs = [{"owner_address": recipient_address, "amount": reward}]
        return self(
            sender_address=None,
            recipient_address=recipient_address,
            amount=reward,
            inputs=[],
            outputs=outputs,
            signature=b""
        )