import sys

def thread_error_exit(func_or_class):
    try:
        return func_or_class
    except Exception as e:
        try:
            open("communication_errors.txt", "a").write(str(e) + "\n")
            exit(1)
        except Exception as e2:
            exit(1)

@thread_error_exit
def is_debug() -> bool:
    return len(sys.argv) >= 2 and sys.argv[1] == "-d"

@thread_error_exit
def log(data: any) -> None:
    with open("communication_log.txt", "a") as f:
        f.write(str(data) + "\n")
    if is_debug():
        print(data)

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
