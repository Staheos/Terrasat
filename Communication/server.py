import socket
import threading
import queue
from util import *
from ServerReceiver import ServerReceiver
from CommunicationClient import CommunicationClient

HOST = 'localhost'
PORT = 1769

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

log(f"Server is listening on {HOST}:{PORT}")

stop_queue = queue.Queue()
packet_queue = queue.Queue()
packet_queue.put("DATA RASPBERRY PI")
log(f"Empty: {packet_queue.qsize()}")
receivers = []

communicationClient = CommunicationClient(stop_queue, packet_queue)
communicationClient.start()

while True:
    log(f"Receivers: {receivers}")
    client_socket, client_address = server_socket.accept()
    # client_thread = threading.Thread(target=client_handler, args=(client_socket,))
    # client_thread.start()
    log(f"Connection from {client_address}")
    receiver = ServerReceiver(client_socket, stop_queue, packet_queue)
    receivers.append(receiver)
    receiver.start()
    if not communicationClient.is_alive():
        log("Communication client is not alive, stopping server.")
        exit(1)

    # while True:
        # print(client_socket.recv(1024).decode("utf-8", errors="strict"))
        # client_socket.close()