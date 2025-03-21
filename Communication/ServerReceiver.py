import threading
import socket
import queue
import Framer
import time

class ServerReceiver(threading.Thread):
    def __init__(self, client_socket: socket.socket, stopq: queue.Queue, out_queue: queue.Queue):
        threading.Thread.__init__(self, args=(), kwargs={})
        self.stopq = stopq
        self.out_queue = out_queue
        self.client_socket = client_socket
        self.daemon = True

    def run(self) -> None:
        framer = Framer()

        while True:
            recv = self.client_socket.recv(16)

            if len(recv) == 0:
                if not self.stopq.empty():
                    break
                time.sleep(0.1)
                continue

            framer.WriteData(recv)
            if not framer.FrameAvailable():
                continue

            res = DeserializeResult(framer.GetFrame())
            print(res.cmd, " ", res.res)
            print("*" + '-' * 50 + "*")
            self.out_queue.put(res.res)