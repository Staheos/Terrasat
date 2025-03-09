def frame(data: str) -> str:
    return "" + data + ""


def get_message_bytes(message: str) -> list[int]:
    # encoded = [ord(c) for c in message]
    # encoded = [255, 255, 0, 0] + encoded + [0]
    # encoded = [255, 255, 0, 0] + message.encode("utf-8", 'ignore') + [0]
    encoded = [255, 255, 0, 0] + [int(b) for b in message.encode("utf-8", 'ignore')] + [0]
    return encoded

def log_inc(data: str) -> None:
    with open("inc.txt", "a") as f:
        f.write(data + "\n")
