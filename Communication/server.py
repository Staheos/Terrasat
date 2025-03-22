import socket
import threading
import queue

from ServerReceiver import ServerReceiver
from CommunicationClient import CommunicationClient

HOST = 'localhost'
PORT = 1769

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server is listening on {HOST}:{PORT}")

stop_queue = queue.Queue()
packet_queue = queue.Queue()
packet_queue.put("DATA RASPBERRY PI")
print(f"Empty: {packet_queue.qsize()}")
receivers = []

communicationClient = CommunicationClient(stop_queue, packet_queue)
communicationClient.start()

while True:
    print(f"Receivers: {receivers}")
    client_socket, client_address = server_socket.accept()
    # client_thread = threading.Thread(target=client_handler, args=(client_socket,))
    # client_thread.start()
    print(f"Connection from {client_address}")
    receiver = ServerReceiver(client_socket, stop_queue, packet_queue)
    receivers.append(receiver)
    receiver.start()

    # while True:
        # print(client_socket.recv(1024).decode("utf-8", errors="strict"))
        # client_socket.close()