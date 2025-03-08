def get_message_bytes(message: str) -> list[int]:
    # encoded = [ord(c) for c in message]
    # encoded = [255, 255, 0, 0] + encoded + [0]
    # encoded = [255, 255, 0, 0] + message.encode("utf-8", 'ignore') + [0]
    encoded = [255, 255, 0, 0] + [int(b) for b in message.encode("utf-8", 'ignore')] + [0]
    return encoded
