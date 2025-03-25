import threading
import socket
import queue
import time

class ServerReceiver(threading.Thread):
    def __init__(self, client_socket: socket.socket, stopq: queue.Queue, packet_queue):
        threading.Thread.__init__(self)
        self.stopq = stopq
        self.packet_queue = packet_queue
        self.client_socket = client_socket
        # self.daemon = True
        self.received = bytearray()

    def run(self) -> None:
        while True:
            recv = self.client_socket.recv(16)

            if len(recv) == 0:
                if not self.stopq.empty():
                    break
                time.sleep(0.1)
                continue
            self.received.extend(recv)

            head = self.received.find(b"HEAD")
            if head == -1:
                continue

            foot = self.received.find(b"FOOT", head)
            if foot == -1:
                continue

            data: bytearray = self.received[head : foot + len(b"FOOT")]
            self.received = self.received[foot + len(b"FOOT"):]
            print(f"Received: {data.decode()}")

            self.packet_queue.put(data.decode())
            print(self.packet_queue.qsize())
            # self.packet_queue.task_done()